import unittest
from llvm.core import (Module, Type, Constant, MetaData)
from .support import TestCase, tests


class TestNamedMetaData(TestCase):
    def test_named_md(self):
        m = Module.new('test_named_md')
        nmd = m.get_or_insert_named_metadata('something')
        md = MetaData.get(m, [Constant.int(Type.int(), 0xbeef)])
        nmd.add(md)
        self.assertTrue(str(nmd).startswith('!something'))
        ir = str(m)
        self.assertTrue('!something' in ir)

tests.append(TestNamedMetaData)

if __name__ == '__main__':
    unittest.main()

