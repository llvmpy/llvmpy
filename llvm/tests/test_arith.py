import unittest
import llvm
from llvm.core import (Module, Type, Builder)
from llvm.ee import EngineBuilder
from .support import TestCase, tests, BITS

class TestArith(TestCase):
    '''
    Test basic arithmetic support with LLVM MCJIT
    '''
    def func_template(self, ty, op):
        m = Module.new('dofjaa')
        fnty = Type.function(ty, [ty, ty])
        fn = m.add_function(fnty, 'foo')
        bldr = Builder.new(fn.append_basic_block(''))
        bldr.ret(getattr(bldr, op)(*fn.args))

        engine = EngineBuilder.new(m).mcjit(True).create()
        ptr = engine.get_pointer_to_function(fn)

        from ctypes import c_uint32, c_uint64, c_float, c_double, CFUNCTYPE

        maptypes = {
            Type.int(32): c_uint32,
            Type.int(64): c_uint64,
            Type.float(): c_float,
            Type.double(): c_double,
        }
        cty = maptypes[ty]
        prototype = CFUNCTYPE(*[cty] * 3)
        callee = prototype(ptr)
        callee(12, 23)

    def template(self, iop, fop):
        inttys = [Type.int(32), Type.int(64)]
        flttys = [Type.float(), Type.double()]

        if iop:
            for ty in inttys:
                self.func_template(ty, iop)
        if fop:
            for ty in flttys:
                self.func_template(ty, fop)

    def test_add(self):
        self.template('add', 'fadd')

    def test_sub(self):
        self.template('sub', 'fsub')

    def test_mul(self):
        self.template('mul', 'fmul')

    def test_div(self):
        if BITS == 32:
            print('skipped test for div')
            print('known failure due to unresolved external symbol __udivdi3')
            return
        self.template('udiv', None) # 'fdiv')

    def test_rem(self):
        if BITS == 32:
            print('skipped test for rem')
            print('known failure due to unresolved external symbol __umoddi3')
            return
        self.template('urem', None) # 'frem')

if llvm.version >= (3, 3):
    # MCJIT is broken in 3.2
    tests.append(TestArith)

if __name__ == '__main__':
    unittest.main()

