#!/usr/bin/env python

#
# This script attempts to achieve 100% function and branch coverage for
# all APIs in the llvm package. It only exercises the APIs, doesn't test
# them for correctness.
#

from llvm import *
from llvm.core import *
from llvm.ee import *
from llvm.passes import *

ti = Type.int()

def do_llvmexception():
    print("    Testing class LLVMException")
    e = LLVMException()


def do_misc():
    print("    Testing miscellaneous functions")
    try:
        load_library_permanently("/usr/lib/libm.so")
    except LLVMException:
        pass
    try:
        print("        ... second one now")
        load_library_permanently("no*such*so")
    except LLVMException:
        pass


def do_llvm():
    print("  Testing module llvm")
    do_llvmexception()
    do_misc()


def do_module():
    print("    Testing class Module")
    m = Module.new('test')
    m.target = 'a'
    a = m.target
    m.data_layout = 'a'
    a = m.data_layout
    # m.add_type_name('a', ti)
    # m.delete_type_name('a')
    Type.struct([ti], name='a')
    m.get_type_named('a').name=''

    s = str(m)
    s = m == Module.new('a')
    m.add_global_variable(ti, 'b')
    m.get_global_variable_named('b')
    gvs = list(m.global_variables)
    ft = Type.function(ti, [ti])
    m.add_function(ft, "func")
    m.get_function_named("func")
    m.get_or_insert_function(ft, "func")
    m.get_or_insert_function(Type.function(ti, []), "func")
    m.get_or_insert_function(ft, "func2")
    fns = list(m.functions)
    try:
        m.verify()
    except LLVMException:
        pass

    class strstream(object):
        def __init__(self):
            self.s = b''

        def write(self, data):
            if not isinstance(data, bytes):
                data = data.encode('utf-8')
            self.s += data

        def read(self):
            return self.s

    ss = strstream()
    m2 = Module.new('test')
    # m2.add_type_name('myint', ti)
    Type.struct([ti], 'myint')

    m2.to_bitcode(ss)
    m3 = Module.from_bitcode(ss)
    t = m2 == m3
    ss2 = strstream()
    ss2.write(str(m))
    m4 = Module.from_assembly(ss2)
    t = m4 == m
    t = m4.pointer_size
    mA = Module.new('ma')
    mB = Module.new('mb')
    mA.link_in(mB)


def do_type():
    print("    Testing class Type")
    for i in range(1,100):
        Type.int(i)
    Type.float()
    Type.double()
    Type.x86_fp80()
    Type.fp128()
    Type.ppc_fp128()
    Type.function(ti, [ti]*100, True)
    Type.function(ti, [ti]*100, False)
    Type.struct([ti]*100)
    Type.packed_struct([ti]*100)
    Type.array(ti, 100)
    ptr = Type.pointer(ti, 4)
    pte = ptr.pointee
    Type.vector(ti, 100)
    Type.void()
    Type.label()

    Type.opaque('an_opaque_type')
    s = str(ti)
    s = ti == Type.float()
    Type.opaque('whatever').set_body([Type.int()])
    s = ti.width
    ft = Type.function(ti, [ti]*10)
    ft.return_type
    ft.vararg
    s = list(ft.args)
    ft.arg_count
    st = Type.struct([ti]*10)
    s = st.element_count
    s = list(st.elements)
    s = st.packed
    st = Type.packed_struct([ti]*10)
    s = st.element_count
    s = list(st.elements)
    s = st.packed
    at = Type.array(ti, 100)
    s = at.element
    s = at.count
    pt = Type.pointer(ti, 10)
    pt.address_space
    vt = Type.vector(ti, 100)
    s = vt.element
    s = vt.count
    Type.int(32) == Type.int(64)
    Type.int(32) != Type.int(64)
    Type.int(32) != Type.float()

### Removed
#def do_typehandle():
#    print("    Testing class TypeHandle")
#    th = TypeHandle.new(Type.opaque())
#    ts = Type.struct([ Type.int(), Type.pointer(th.type) ])
#    th.type.refine(ts)


def do_value():
    print("    Testing class Value")
    k = Constant.int(ti, 42)
    k.name = 'a'
    s = k.name
    t = k.type
    s = str(k)
    s = k == Constant.int(ti, 43)
    i = k.value_id
    i = k.use_count
    i = k.uses


def do_user():
    m = Module.new('a')
    ft = Type.function(ti, [ti]*2)
    f = Function.new(m, ft, 'func')
    b = f.append_basic_block('a')
    bb = Builder.new(b)
    i1 = bb.add(f.args[0], f.args[1])
    i2 = bb.ret(i1)
    i1.operand_count == 2
    i2.operand_count == 1
    i1.operands[0] is f.args[0]
    i1.operands[1] is f.args[1]
    i2.operands[0] is i1


def do_constant():
    print("    Testing class Constant")
    Constant.null(ti)
    Constant.all_ones(ti)
    Constant.undef(ti)
    Constant.int(ti, 10)
    Constant.int_signextend(ti, 10)
    Constant.real(Type.float(), "10.0")
    Constant.real(Type.float(), 3.14)
    Constant.string("test")
    Constant.stringz("test2")
    Constant.array(ti, [Constant.int(ti,42)]*10)
    Constant.struct([Constant.int(ti,42)]*10)
    Constant.packed_struct([Constant.int(ti,42)]*10)
    Constant.vector([Constant.int(ti,42)]*10)

    Constant.sizeof(ti)

    k = Constant.int(ti, 10)
    f = Constant.real(Type.float(), 3.1415)
    k.neg().not_().add(k).sub(k).mul(k).udiv(k).sdiv(k).urem(k)
    k.srem(k).and_(k).or_(k).xor(k).icmp(IPRED_ULT, k)
    f.fdiv(f).frem(f).fcmp(RPRED_ULT, f)
    f.fadd(f).fmul(f).fsub(f)
    vi = Constant.vector([Constant.int(ti,42)]*10)
    vf = Constant.vector([Constant.real(Type.float(), 3.14)]*10)
    k.shl(k).lshr(k).ashr(k)
    return
    # TODO gep
    k.trunc(Type.int(1))
    k.sext(Type.int(64))
    k.zext(Type.int(64))
    Constant.real(Type.double(), 1.0).fptrunc(Type.float())
    Constant.real(Type.float(), 1.0).fpext(Type.double())
    k.uitofp(Type.float())
    k.sitofp(Type.float())
    f.fptoui(ti)
    f.fptosi(ti)
    p = Type.pointer(ti)
    # TODO ptrtoint
    k.inttoptr(p)
    f.bitcast(Type.int(32))
    k.trunc(Type.int(1)).select(k, k)
    vi.extract_element( Constant.int(ti,0) )
    vi.insert_element( k, k )
    vi.shuffle_vector( vi, vi )


def do_global_value():
    print("    Testing class GlobalValue")
    m = Module.new('a')
    gv = GlobalVariable.new(m, Type.int(), 'b')
    s = gv.is_declaration
    m = gv.module
    gv.linkage = LINKAGE_EXTERNAL
    s = gv.linkage
    gv.section = '.text'
    s = gv.section
    gv.visibility = VISIBILITY_HIDDEN
    s = gv.visibility
    gv.alignment = 8
    s = gv.alignment


def do_global_variable():
    print("    Testing class GlobalVariable")
    m = Module.new('a')
    gv = GlobalVariable.new(m, Type.int(), 'b')
    gv = GlobalVariable.get(m, 'b')
    gv.delete()
    gv = GlobalVariable.new(m, Type.int(), 'c')
    gv.initializer = Constant.int( ti, 10 )
    s = gv.initializer
    gv.global_constant = True
    s = gv.global_constant


def do_argument():
    print("    Testing class Argument")
    m = Module.new('a')
    tip = Type.pointer(ti)
    ft = Type.function(tip, [tip])
    f = Function.new(m, ft, 'func')
    a = f.args[0]
    a.add_attribute(ATTR_NEST)
    a.remove_attribute(ATTR_NEST)
    a.alignment = 16
    a1 = a.alignment


def do_function():
    print("    Testing class Function")
    ft = Type.function(ti, [ti]*20)
    zz = Function.new(Module.new('z'), ft, 'foobar')
    del zz
    Function.new(Module.new('zz'), ft, 'foobar')
    m = Module.new('a')
    f = Function.new(m, ft, 'func')
    f.delete()
    ft = Type.function(ti, [ti]*20)
    f = Function.new(m, ft, 'func2')
    has_nounwind = f.does_not_throw
    f.does_not_throw = True
    f2 = Function.intrinsic(m, INTR_COS, [ti])
    g = f.intrinsic_id
    f.calling_convenion = CC_FASTCALL
    g = f.calling_convenion
    f.collector = 'a'
    c = f.collector
    a = list(f.args)
    g = f.basic_block_count
#    g = f.entry_basic_block
#    g = f.append_basic_block('a')
#    g = f.entry_basic_block
    g = list(f.basic_blocks)
    f.add_attribute(ATTR_NO_RETURN)
    f.add_attribute(ATTR_ALWAYS_INLINE)
    #for some reason removeFnAttr is just gone in 3.3
    if version <= (3, 2):
        f.remove_attribute(ATTR_NO_RETURN)

    # LLVM misbehaves:
    #try:
    #    f.verify()
    #except LLVMException:
    #    pass


def do_instruction():
    print("    Testing class Instruction")
    m = Module.new('a')
    ft = Type.function(ti, [ti]*20)
    f = Function.new(m, ft, 'func')
    b = f.append_basic_block('a')
    bb = Builder.new(b)
    i = bb.ret_void()
    bb2 = i.basic_block
    ops = i.operands
    opcount = i.operand_count


def do_callorinvokeinstruction():
    print("    Testing class CallOrInvokeInstruction")
    m = Module.new('a')
    ft = Type.function(ti, [ti])
    f = Function.new(m, ft, 'func')
    b = f.append_basic_block('a')
    bb = Builder.new(b)
    i = bb.invoke(f, [Constant.int(ti, 10)], b, b)
    a = i.calling_convention
    i.calling_convention = CC_FASTCALL
    if version <= (3, 2):
        i.add_parameter_attribute(0, ATTR_SEXT)
        i.remove_parameter_attribute(0, ATTR_SEXT)
        i.set_parameter_alignment(0, 8)
    #tc = i.tail_call
    #i.tail_call = 1


def do_phinode():
    print("    Testing class PhiNode")
    m = Module.new('a')
    ft = Type.function(ti, [ti])
    f = Function.new(m, ft, 'func')
    b = f.append_basic_block('b')
    c = f.append_basic_block('c')
    d = f.append_basic_block('d')
    bb = Builder.new(d)
    p = bb.phi(ti)
    v = p.incoming_count
    p.add_incoming( Constant.int(ti, 10), b )
    p.add_incoming( Constant.int(ti, 10), c )
    p.get_incoming_value(0)
    p.get_incoming_block(0)


def do_switchinstruction():
    print("    Testing class SwitchInstruction")
    m = Module.new('a')
    ft = Type.function(ti, [ti])
    f = Function.new(m, ft, 'func')
    b = f.append_basic_block('b')
    bb = Builder.new(b)
    s = bb.switch(f.args[0], b)
    s.add_case(Constant.int(ti, 10), b)


def do_basicblock():
    print("    Testing class BasicBlock")
    m = Module.new('a')
    ft = Type.function(ti, [ti])
    f = Function.new(m, ft, 'func')
    b = f.append_basic_block('b')
    bb = Builder.new(b)
    s = bb.switch(f.args[0], b)
    s.add_case(Constant.int(ti, 10), b)
    s = list(b.instructions)
    b2 = b.insert_before('before')
    b2.delete()
    ff = b.function
    m2 = ff.module
    t = m == m2


def _do_builder_mrv():
    m = Module.new('mrv')
    ft = Type.function(Type.array(ti, 2), [ti])
    f = Function.new(m, ft, 'divrem')
    blk = f.append_basic_block('b')
    b = Builder.new(blk)
    v = b.call(f, [Constant.int(ti, 1)])
    v1 = b.extract_value(v, 0)
    v2 = b.extract_value(v, 1)
    b.ret_many([v1, v2])
    #print f


def do_builder():
    print("    Testing class Builder")
    m = Module.new('a')
    ft = Type.function(ti, [ti])
    f = Function.new(m, ft, 'func')
    blk = f.append_basic_block('b')
    b = Builder.new(blk)
    b.ret(Constant.int(ti, 10))
    b.position_at_beginning(blk)
    b.position_at_end(blk)
    b.position_before(blk.instructions[0])
    blk2 = b.basic_block
    b.ret_void()
    b.ret(Constant.int(ti, 10))
    _do_builder_mrv()
    #b.ret_many([Constant.int(ti, 10)]*10)
    b.branch(blk)
    b.cbranch(Constant.int(Type.int(1), 1), blk, blk)
    b.switch(f.args[0], blk)
    b.invoke(f, [Constant.int(ti,10)], blk, blk)
    # b.unwind() # removed
    b.unreachable()
    v = f.args[0]
    fv = Constant.real(Type.float(), "1.0")
    k = Constant.int(ti, 10)
    b.add(v, v)
    b.fadd(fv, fv)
    b.sub(v, v)
    b.fsub(fv, fv)
    b.mul(v, v)
    b.fmul(fv, fv)
    b.udiv(v, v)
    b.sdiv(v, v)
    b.fdiv(fv, fv)
    b.urem(v, v)
    b.srem(v, v)
    b.frem(fv, fv)
    b.shl(v, k)
    b.lshr(v, k)
    b.ashr(v, k)
    b.and_(v, v)
    b.or_(v, v)
    b.xor(v, v)
    b.neg(v)
    b.not_(v)
    p = b.malloc(Type.int())
    b.malloc_array(Type.int(), k)
    b.alloca(Type.int())
    b.alloca_array(Type.int(), k)
    b.free(p)
    b.load(p)
    b.store(k, p)
    # TODO gep
    b.trunc(v, Type.int(1))
    b.zext(v, Type.int(64))
    b.sext(v, Type.int(64))
    b.fptoui(fv, ti)
    b.fptosi(fv, ti)
    b.uitofp(k, Type.float())
    b.sitofp(k, Type.float())
    b.fptrunc(Constant.real(Type.double(), "1.0"), Type.float())
    b.fpext(Constant.real(Type.float(), "1.0"), Type.double())
    b.ptrtoint(p, ti)
    b.inttoptr(k, Type.pointer(Type.int()))
    b.bitcast(v, Type.float())
    b.icmp(IPRED_ULT, v, v)
    b.fcmp(RPRED_ULT, fv, fv)
    vi = Constant.vector([Constant.int(ti,42)]*10)
    vi_mask = Constant.vector([Constant.int(ti, X) for X in range(20)])
    vf = Constant.vector([Constant.real(Type.float(), 3.14)]*10)
    # TODO b.extract_value(v, 0)
    b.call(f, [v])
    b.select(Constant.int(Type.int(1), 1), blk, blk)
    b.vaarg(v, Type.int())
    b.extract_element(vi, v)
    b.insert_element(vi, v, v)
    b.shuffle_vector(vi, vi, vi_mask)
    # NOTE: phi nodes without incoming values segfaults in LLVM during
    # destruction.
    i = b.phi(Type.int())
    i.add_incoming(v, blk)
    t = i.is_terminator == False
    t = i.is_binary_op == False
    t = i.is_shift == False
    t = i.is_cast == False
    t = i.is_logical_shift == False
    t = i.is_arithmetic_shift == False
    t = i.is_associative == False
    t = i.is_commutative == False
    t = i.is_volatile == False
    t = i.opcode
    t = i.opcode_name


def do_llvm_core():
    print("  Testing module llvm.core")
    do_module()
    do_type()
    #    do_typehandle()
    do_value()
    do_user()
    do_constant()
    do_global_value()
    do_global_variable()
    do_argument()
    do_function()
    do_instruction()
    do_callorinvokeinstruction()
    do_phinode()
    do_switchinstruction()
    do_basicblock()
    do_builder()


def do_targetdata():
    print("    Testing class TargetData")
    t = TargetData.new('')
    v = str(t)
    v = t.byte_order
    v = t.pointer_size
    v = t.target_integer_type
    ty = Type.int()
    v = t.size(ty)
    v = t.store_size(ty)
    v = t.abi_size(ty)
    v = t.abi_alignment(ty)
    v = t.callframe_alignment(ty)
    v = t.preferred_alignment(ty)
    sty = Type.struct([ty, ty])
    v = t.element_at_offset(sty, 0)
    v = t.offset_of_element(sty, 0)
    m = Module.new('a')
    gv = m.add_global_variable(ty, 'gv')
    v = t.preferred_alignment(gv)


def do_genericvalue():
    print("    Testing class GenericValue")
    v = GenericValue.int(ti, 1)
    v = GenericValue.int_signed(ti, 1)
    v = GenericValue.real(Type.float(), 3.14)
    a = v.as_int()
    a = v.as_int_signed()
    a = v.as_real(Type.float())


def do_executionengine():
    print("    Testing class ExecutionEngine")
    m = Module.new('a')
    ee = ExecutionEngine.new(m, False) # True)
    ft = Type.function(ti, [])
    f = m.add_function(ft, 'func')
    bb = f.append_basic_block('entry')
    b = Builder.new(bb)
    b.ret(Constant.int(ti, 42))
    ee.run_static_ctors()
    gv = ee.run_function(f, [])
    is42 = gv.as_int() == 42
    ee.run_static_dtors()
    ee.free_machine_code_for(f)
    t = ee.target_data
    m2 = Module.new('b')
    ee.add_module(m2)
    m3 = Module.new('c')
    ee2 = ExecutionEngine.new(m3, False)
    m4 = Module.new('d')
    m5 = Module.new('e')
    #ee3 = ExecutionEngine.new(m4, False)
    #ee3.add_module(m5)
    #x = ee3.remove_module(m5)
    #isinstance(x, Module)


def do_llvm_ee():
    print("  Testing module llvm.ee")
    do_targetdata()
    do_genericvalue()
    do_executionengine()


def do_passmanager():
    print("    Testing class PassManager")
    pm = PassManager.new()
    pm.add(TargetData.new(''))

    print('.........Begging for rewrite!!!')
    ### It is not practical to maintain all PASS_* constants.
    #
    #    passes = ('PASS_OPTIMAL_EDGE_PROFILER', 'PASS_EDGE_PROFILER',
    #              'PASS_PROFILE_LOADER', 'PASS_AAEVAL')
    #    all_these = [getattr(llvm.passes, x)
    #                    for x in dir(llvm.passes)
    #                        if x.startswith('PASS_') and x not in passes]
    #    for i in all_these:
    #        print i
    #        pm.add(i)
    pm.run(Module.new('a'))


def do_functionpassmanager():
    print("    Testing class FunctionPassManager")
    m = Module.new('a')
    ft = Type.function(ti, [])
    f = m.add_function(ft, 'func')
    bb = f.append_basic_block('entry')
    b = Builder.new(bb)
    b.ret(Constant.int(ti, 42))
    fpm = FunctionPassManager.new(m)
    fpm.add(TargetData.new(''))
    fpm.add(PASS_ADCE)
    fpm.initialize()
    fpm.run(f)
    fpm.finalize()


def do_llvm_passes():
    print("  Testing module llvm.passes")
    do_passmanager()
    do_functionpassmanager()

def do_llvm_target():
    print("  Testing module llvm.target")
    from llvm import target

    target.initialize_all()
    target.print_registered_targets()
    target.get_host_cpu_name()
    target.get_default_triple()

    tm = TargetMachine.new()
    tm = TargetMachine.lookup("arm")
    tm = TargetMachine.arm()
    tm = TargetMachine.thumb()
    tm = TargetMachine.x86()
    tm = TargetMachine.x86_64()
    tm.target_data
    tm.target_name
    tm.target_short_description
    tm.triple
    tm.cpu
    tm.feature_string
    tm.target

    if llvm.version >= (3, 4):
         tm.reg_info
         tm.subtarget_info
         tm.asm_info
         tm.instr_info
         tm.instr_analysis
         tm.disassembler
         tm.is_little_endian()

def do_llvm_mc():
    if llvm.version < (3, 4):
        return

    from llvm import target
    from llvm import mc

    target.initialize_all()
    tm = TargetMachine.x86()
    dasm = mc.Disassembler(tm)

    for (offset, data, instr) in dasm.decode("c3", 0):
        pass

def main():
    print("Testing package llvm")
    do_llvm()
    do_llvm_core()
    do_llvm_ee()
    do_llvm_passes()
    do_llvm_target()
    do_llvm_mc()

if __name__ == '__main__':
    main()

# to add:
# IntegerType
# FunctionType
# StructType
# ArrayType
# PointerType
# VectorType
# ConstantExpr
# ConstantAggregateZero
# ConstantInt
# ConstantFP
# ConstantArray
# ConstantStruct
# ConstantVector
# ConstantPointerNull
# MemoryBuffer

