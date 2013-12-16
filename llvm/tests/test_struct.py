import unittest
from llvm.core import Type, Module, Builder, Constant
from .support import TestCase, tests

class TestStruct(TestCase):
    def test_struct_identical(self):
        ta = Type.struct([Type.int(32), Type.float()], name='ta')
        tb = Type.struct([Type.int(32), Type.float()])
        self.assertTrue(ta.is_layout_identical(tb))

    def test_struct_extract_value_2d(self):
        ta = Type.struct([Type.int(32), Type.float()])
        tb = Type.struct([ta, Type.float()])
        m = Module.new('')
        f = m.add_function(Type.function(Type.void(), []), "foo")
        b = Builder.new(f.append_basic_block(''))
        v = Constant.undef(tb)
        ins = b.insert_value(v, Constant.real(Type.float(), 1.234), [0, 1])
        ext = b.extract_value(ins, [0, 1])
        b.ret_void()
        m.verify()
        self.assertEqual(str(ext), 'float 0x3FF3BE76C0000000')

tests.append(TestStruct)

if __name__ == '__main__':
    unittest.main()

