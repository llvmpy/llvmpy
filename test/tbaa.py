from llvm.core import *
from llvm.tbaa import *
from llvm.tests.support import TestCase
import unittest

class TestTBAABuilder(TestCase):
    def test_tbaa_builder(self):
        mod = Module.new('test_tbaa_builder')
        fty = Type.function(Type.void(), [Type.pointer(Type.float())])
        foo = mod.add_function(fty, 'foo')
        bb = foo.append_basic_block('entry')
        bldr = Builder.new(bb)

        tbaa = TBAABuilder.new(mod, "tbaa.root")
        float = tbaa.get_node('float', const=False)
        const_float = tbaa.get_node('const float', float, const=True)


        tbaa = TBAABuilder.new(mod, "tbaa.root")
        old_const_float = const_float
        del const_float

        const_float = tbaa.get_node('const float', float, const=True)

        self.assertIs(old_const_float, const_float)

        ptr = bldr.load(foo.args[0])
        ptr.set_metadata('tbaa', const_float)


        bldr.ret_void()
        print(mod)

if __name__ == '__main__':
    unittest.main()
