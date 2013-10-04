import unittest
from llvm.core import (Module, Type, Constant, MetaData, MetaDataString)
from .support import TestCase, tests

class TestMetaData(TestCase):
    # test module metadata
    def test_metadata(self):
        m = Module.new('a')
        t = Type.int()
        metadata = MetaData.get(m, [Constant.int(t, 100),
                                    MetaDataString.get(m, 'abcdef'),
                                    None])
        MetaData.add_named_operand(m, 'foo', metadata)
        self.assertEqual(MetaData.get_named_operands(m, 'foo'), [metadata])
        self.assertEqual(MetaData.get_named_operands(m, 'bar'), [])
        self.assertEqual(len(metadata.operands), 3)
        self.assertEqual(metadata.operands[0].z_ext_value, 100)
        self.assertEqual(metadata.operands[1].string, 'abcdef')
        self.assertTrue(metadata.operands[2] is None)

tests.append(TestMetaData)

if __name__ == '__main__':
    unittest.main()

