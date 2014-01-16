from __future__ import print_function, absolute_import
import sys
from llvm.core import Type, Function, Builder, Module
import llvm.core as lc
import llvm.ee as le
import multiprocessing
from ctypes import *

INTRINSICS = {}

CTYPES_MAP = {
    Type.int(): c_int32,
    Type.int(64): c_int64,
    Type.float(): c_float,
    Type.double(): c_double,
}


def register(name, retty, *args):
    def wrap(fn):
        INTRINSICS[name] = (retty, args), fn
        return fn
    return wrap


def intr_impl(intrcode, *types):
    def impl(module, builder, args):
        intr = Function.intrinsic(module, intrcode, types)
        r = builder.call(intr, args)
        return r
    return impl


register("llvm.powi.f64", Type.double(), Type.double(), Type.int())\
        (intr_impl(lc.INTR_POWI, Type.double()))

register("llvm.powi.f32", Type.float(), Type.float(), Type.int())\
        (intr_impl(lc.INTR_POWI, Type.float()))

register("llvm.pow.f64", Type.double(), Type.double(), Type.double())\
        (intr_impl(lc.INTR_POW, Type.double()))

register("llvm.pow.f32", Type.float(), Type.float(), Type.float())\
        (intr_impl(lc.INTR_POW, Type.float()))

register("llvm.sin.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_SIN, Type.double()))

register("llvm.sin.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_SIN, Type.float()))

register("llvm.cos.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_COS, Type.double()))

register("llvm.cos.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_COS, Type.float()))

register("llvm.log.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_LOG, Type.double()))

register("llvm.log.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_LOG, Type.float()))

register("llvm.log2.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_LOG2, Type.double()))

register("llvm.log2.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_LOG2, Type.float()))

register("llvm.log10.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_LOG10, Type.double()))

register("llvm.log10.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_LOG10, Type.float()))

register("llvm.sqrt.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_SQRT, Type.double()))

register("llvm.sqrt.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_SQRT, Type.float()))

register("llvm.exp.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_EXP, Type.double()))

register("llvm.exp.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_EXP, Type.float()))

register("llvm.exp2.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_EXP2, Type.double()))

register("llvm.exp2.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_EXP2, Type.float()))

register("llvm.fabs.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_FABS, Type.double()))

register("llvm.fabs.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_FABS, Type.float()))

register("llvm.floor.f64", Type.double(), Type.double())\
        (intr_impl(lc.INTR_FLOOR, Type.double()))

register("llvm.floor.f32", Type.float(), Type.float())\
        (intr_impl(lc.INTR_FLOOR, Type.float()))


def build_test(name):
    (retty, args), impl = INTRINSICS[name]
    module = Module.new("test.%s" % name)
    fn = module.add_function(Type.function(retty, args), name="test_%s" % name)
    builder = Builder.new(fn.append_basic_block(""))
    retval = impl(module, builder, fn.args)
    builder.ret(retval)
    fn.verify()
    module.verify()
    return module, fn


def run_test(name):
    module, fn = build_test(name)
    eb = le.EngineBuilder.new(module).mcjit(True)
    engine = eb.create()
    ptr = engine.get_pointer_to_function(fn)

    argtys = fn.type.pointee.args
    retty = fn.type.pointee.return_type
    cargtys = [CTYPES_MAP[a] for a in argtys]
    cretty = CTYPES_MAP[retty]
    cfunc = CFUNCTYPE(cretty, *cargtys)(ptr)
    args = [1] * len(cargtys)
    cfunc(*args)


def spawner(name):
    print("Testing %s" % name)
    proc = multiprocessing.Process(target=run_test, args=(name,))

    print('-' * 80)
    proc.start()
    proc.join()

    if proc.exitcode != 0:
        print("FAILED")
        ok = False
    else:
        print("PASSED")
        ok = True
    print('=' * 80)
    print()

    return ok

USAGE = """
Args: [name]

name: intrinsic name to test

If no name is given, test all intrinsics.

"""


def main(argv=()):
    if len(argv) == 1:
        intrname = argv[1]
        spawner(intrname)
    elif not argv:
        failed = []
        for name in sorted(INTRINSICS):
            if not spawner(name):
                failed.append(name)

        print("Summary:")
        for name in failed:
            print("%s failed" % name)
    else:
        print(USAGE)


if __name__ == '__main__':
    main(argv=sys.argv[1:])
