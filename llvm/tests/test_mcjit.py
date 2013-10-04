import unittest
import sys
import llvm
from llvm.core import (Module, Type, Builder)
from llvm.ee import EngineBuilder

import llvm.ee as le
from .support import TestCase, tests, BITS

class TestMCJIT(TestCase):
    def test_mcjit(self):
        m = Module.new('oidfjs')
        fnty = Type.function(Type.int(), [Type.int(), Type.int()])
        func = m.add_function(fnty, 'foo')
        bb = func.append_basic_block('')
        bldr = Builder.new(bb)
        bldr.ret(bldr.add(*func.args))

        func.verify()

        engine = EngineBuilder.new(m).mcjit(True).create()
        ptr = engine.get_pointer_to_function(func)

        from ctypes import c_int, CFUNCTYPE
        callee = CFUNCTYPE(c_int, c_int, c_int)(ptr)
        self.assertEqual(321 + 123, callee(321, 123))

    def test_multi_module_linking(self):
        # generate external library module
        m = Module.new('external-library-module')
        fnty = Type.function(Type.int(), [Type.int(), Type.int()])
        libfname = 'myadd'
        func = m.add_function(fnty, libfname)
        bb = func.append_basic_block('')
        bldr = Builder.new(bb)
        bldr.ret(bldr.add(*func.args))
        func.verify()

        # JIT the lib module and bind dynamic symbol
        libengine = EngineBuilder.new(m).mcjit(True).create()
        myadd_ptr = libengine.get_pointer_to_function(func)
        le.dylib_add_symbol(libfname, myadd_ptr)

        # reference external library
        m = Module.new('user')
        fnty = Type.function(Type.int(), [Type.int(), Type.int()])
        func = m.add_function(fnty, 'foo')
        bb = func.append_basic_block('')
        bldr = Builder.new(bb)
        extadd = m.get_or_insert_function(fnty, name=libfname)
        bldr.ret(bldr.call(extadd, func.args))
        func.verify()

        # JIT the user module
        engine = EngineBuilder.new(m).mcjit(True).create()
        ptr = engine.get_pointer_to_function(func)
        self.assertEqual(myadd_ptr,
                         engine.get_pointer_to_named_function(libfname))

        from ctypes import c_int, CFUNCTYPE
        callee = CFUNCTYPE(c_int, c_int, c_int)(ptr)
        self.assertEqual(321 + 123, callee(321, 123))


if (llvm.version >= (3, 3) and
    not (sys.platform.startswith('win32') and BITS == 64)):
    # MCJIT broken in 3.2, the test will segfault in OSX?
    # Compatbility problem on windows 7 64-bit?
    tests.append(TestMCJIT)

if __name__ == '__main__':
    unittest.main()

