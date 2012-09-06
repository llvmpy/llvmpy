import unittest

from llvm.core import *

class TestMetaData(unittest.TestCase):
    def test_metadata_get(self):
        module = Module.new('test_metadata')
        md = MetaData.get(module, [Constant.int(Type.int(), 1234)])

    def test_meta_load_nt(self):
        module = Module.new('test_meta_load_nt')
        func = module.add_function(Type.function(Type.void(), []),
                                   name='test_load_nt')
        bldr = Builder.new(func.append_basic_block('entry'))
        addr = Constant.int(Type.int(), 0xdeadbeef)
        loadinst = bldr.load(bldr.inttoptr(addr, Type.pointer(Type.int(8))))

        md = MetaData.get(module, [Constant.int(Type.int(), 1)])
        loadinst.set_metadata('nontemporal', md)

        bldr.ret_void()
        module.verify()

        self.assertIn('!nontemporal', str(loadinst))

if __name__ == '__main__':
    unittest.main()

