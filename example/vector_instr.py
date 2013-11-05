'''
This example shows:
1) how to use vector instructions
2) how to take advantage of LLVM loop vectorization to transform scalar     
   operations to vector operations
'''

from __future__ import print_function
import llvm.core as lc
import llvm.ee as le
import llvm.passes as lp
from ctypes import CFUNCTYPE, POINTER, c_int, c_float

def build_manual_vector():
    mod = lc.Module.new('manual.vector')
    intty = lc.Type.int(32)
    vecty = lc.Type.vector(lc.Type.float(), 4)
    aryty = lc.Type.pointer(lc.Type.float())
    fnty = lc.Type.function(lc.Type.void(), [aryty, aryty, aryty, intty])
    fn = mod.add_function(fnty, name='vector_add')
    bbentry = fn.append_basic_block('entry')
    bbloopcond = fn.append_basic_block('loop.cond')
    bbloopbody = fn.append_basic_block('loop.body')
    bbexit = fn.append_basic_block('exit')
    builder = lc.Builder.new(bbentry)

    # populate function body
    in1, in2, out, size = fn.args
    ZERO = lc.Constant.null(intty)
    loopi_ptr = builder.alloca(intty)
    builder.store(ZERO, loopi_ptr)

    builder.branch(bbloopcond)
    builder.position_at_end(bbloopcond)

    loopi = builder.load(loopi_ptr)
    loopcond = builder.icmp(lc.ICMP_ULT, loopi, size)

    builder.cbranch(loopcond, bbloopbody, bbexit)
    builder.position_at_end(bbloopbody)

    vecaryty = lc.Type.pointer(vecty)
    in1asvec = builder.bitcast(builder.gep(in1, [loopi]), vecaryty)
    in2asvec = builder.bitcast(builder.gep(in2, [loopi]), vecaryty)
    outasvec = builder.bitcast(builder.gep(out, [loopi]), vecaryty)

    vec1 = builder.load(in1asvec)
    vec2 = builder.load(in2asvec)

    vecout = builder.fadd(vec1, vec2)

    builder.store(vecout, outasvec)

    next = builder.add(loopi, lc.Constant.int(intty, 4))
    builder.store(next, loopi_ptr)

    builder.branch(bbloopcond)
    builder.position_at_end(bbexit)

    builder.ret_void()

    return mod, fn


def build_auto_vector():
    mod = lc.Module.new('auto.vector')
    # Loop vectorize is sensitive to the size of the index size(!?)
    intty = lc.Type.int(tuple.__itemsize__ * 8)
    aryty = lc.Type.pointer(lc.Type.float())
    fnty = lc.Type.function(lc.Type.void(), [aryty, aryty, aryty, intty])
    fn = mod.add_function(fnty, name='vector_add')
    bbentry = fn.append_basic_block('entry')
    bbloopcond = fn.append_basic_block('loop.cond')
    bbloopbody = fn.append_basic_block('loop.body')
    bbexit = fn.append_basic_block('exit')
    builder = lc.Builder.new(bbentry)

    # populate function body
    in1, in2, out, size = fn.args
    in1.add_attribute(lc.ATTR_NO_ALIAS)
    in2.add_attribute(lc.ATTR_NO_ALIAS)
    out.add_attribute(lc.ATTR_NO_ALIAS)
    ZERO = lc.Constant.null(intty)
    loopi_ptr = builder.alloca(intty)
    builder.store(ZERO, loopi_ptr)

    builder.branch(bbloopcond)
    builder.position_at_end(bbloopcond)

    loopi = builder.load(loopi_ptr)
    loopcond = builder.icmp(lc.ICMP_ULT, loopi, size)

    builder.cbranch(loopcond, bbloopbody, bbexit)
    builder.position_at_end(bbloopbody)

    in1elem = builder.load(builder.gep(in1, [loopi]))
    in2elem = builder.load(builder.gep(in2, [loopi]))

    outelem = builder.fadd(in1elem, in2elem)

    builder.store(outelem, builder.gep(out, [loopi]))

    next = builder.add(loopi, lc.Constant.int(intty, 1))
    builder.store(next, loopi_ptr)

    builder.branch(bbloopcond)
    builder.position_at_end(bbexit)

    builder.ret_void()

    return mod, fn

def example(title, module_builder, opt):
    print(title.center(80, '='))
    mod, fn = module_builder()

    eb = le.EngineBuilder.new(mod).opt(3)
    if opt:
        print('opt')
        tm = eb.select_target()
        pms = lp.build_pass_managers(mod=mod, tm=tm, opt=3, loop_vectorize=True,
                                     fpm=False)
        pms.pm.run(mod)

    print(mod)
    print(mod.to_native_assembly())

    engine = eb.create()
    ptr = engine.get_pointer_to_function(fn)

    callable = CFUNCTYPE(None, POINTER(c_float), POINTER(c_float),
                         POINTER(c_float), c_int)(ptr)

    N = 20
    in1 = (c_float * N)(*range(N))
    in2 = (c_float * N)(*range(N))
    out = (c_float * N)()

    print('in1: ', list(in1))
    print('in1: ', list(in2))

    callable(in1, in2, out, N)

    print('out', list(out))


def main():
    example('manual vector function', build_manual_vector, False)
    example('auto vector function', build_auto_vector, True)

if __name__ == '__main__':
    main()
