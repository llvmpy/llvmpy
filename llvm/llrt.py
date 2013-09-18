import os
import llvm.core as lc
import llvm.passes as lp
import llvm.ee as le

def replace_divmod64(lfunc):
    '''Replaces all 64-bit integer division (sdiv, udiv) and modulo (srem, urem)
    '''
    int64 = lc.Type.int(64)
    int64ptr = lc.Type.pointer(lc.Type.int(64))

    functy = lc.Type.function(int64, [int64, int64])
    udiv64 = lfunc.module.get_or_insert_function(functy, '__llrt_udiv64')
    sdiv64 = lfunc.module.get_or_insert_function(functy, '__llrt_sdiv64')
    umod64 = lfunc.module.get_or_insert_function(functy, '__llrt_umod64')
    smod64 = lfunc.module.get_or_insert_function(functy, '__llrt_smod64')

    builder = lc.Builder.new(lfunc.entry_basic_block)
    for bb in lfunc.basic_blocks:
        for inst in bb.instructions:
            if inst.opcode_name == 'sdiv' and inst.type == int64:
                _replace_with(builder, inst, sdiv64)
            elif inst.opcode_name == 'udiv' and inst.type == int64:
                _replace_with(builder, inst, udiv64)
            elif inst.opcode_name == 'srem' and inst.type == int64:
                _replace_with(builder, inst, smod64)
            elif inst.opcode_name == 'urem' and inst.type == int64:
                _replace_with(builder, inst, umod64)

def _replace_with(builder, inst, func):
    '''Replace instruction with a call to the function with the same operands
    as arguments.
    '''
    builder.position_before(inst)
    replacement = builder.call(func, inst.operands)
    inst.replace_all_uses_with(replacement._ptr)
    inst.erase_from_parent()

def load(arch):
    '''Load the LLRT module corresponding to the given architecture
    Creates a new module and optimizes it using the information from
    the host machine.
    '''
    if arch != 'x86_64':
        arch = 'x86'
    path = os.path.join(os.path.dirname(__file__), 'llrt', 'llrt_%s.ll' % arch)
    with open(path) as fin:
        lib = lc.Module.from_assembly(fin)

    # run passes to optimize
    tm = le.TargetMachine.new()
    pms = lp.build_pass_managers(tm, opt=3, fpm=False)
    pms.pm.run(lib)
    return lib

class LLRT(object):
    def __init__(self):
        arch = le.get_default_triple().split('-', 1)[0]
        self.module = load(arch)
        self.engine = le.EngineBuilder.new(self.module).opt(3).create()
        self.installed_symbols = set()

    def install_symbols(self):
        '''Bind all the external symbols to the global symbol map.
        Any future reference to these symbols will be automatically resolved
        by LLVM.
        '''
        for lfunc in self.module.functions:
            if lfunc.linkage == lc.LINKAGE_EXTERNAL:
                mangled = '__llrt_' + lfunc.name
                self.installed_symbols.add(mangled)
                ptr = self.engine.get_pointer_to_function(lfunc)
                le.dylib_add_symbol(mangled, ptr)

    def uninstall_symbols(self):
        for sym in self.installed_symbols:
            le.dylib_add_symbol(sym, 0)


