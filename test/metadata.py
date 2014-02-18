from __future__ import print_function

import unittest
from llvm.tests.support import TestCase
from llvm.core import *

class TestMetaData(TestCase):
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

    def test_meta_load_invariant(self):
        module = Module.new('test_meta_load_invariant')
        func = module.add_function(Type.function(Type.void(), []),
                                   name='test_load_invariant')
        bldr = Builder.new(func.append_basic_block('entry'))
        addr = Constant.int(Type.int(), 0xdeadbeef)
        loadinst = bldr.load(bldr.inttoptr(addr, Type.pointer(Type.int(8))),
                             invariant=True)

        bldr.ret_void()
        module.verify()

        self.assertIn('!invariant.load', str(loadinst))

    def test_tbaa_metadata(self):
        '''just a simple excerise of the code
        '''
        mod = Module.new('test_tbaa_metadata')
        root = MetaData.get(mod, [MetaDataString.get(mod, "root")])
        MetaData.add_named_operand(mod, 'tbaa', root)

        ops = [MetaDataString.get(mod, "int"), root]
        md1 = MetaData.get(mod, ops)
        MetaData.add_named_operand(mod, 'tbaa', md1)
        print(md1)

        ops = [MetaDataString.get(mod, "const float"),
               root,
               Constant.int(Type.int(64), 1)]

        md2 = MetaData.get(mod, ops)
        MetaData.add_named_operand(mod, 'tbaa', md2)
        print(md2)

        print(mod)


if __name__ == '__main__':
    unittest.main()

