from __future__ import print_function
import unittest
from llvm.core import Type
from llvm.ee import TargetMachine
from llvm.abi import DefaultABIInfo
from .support import TestCase, tests

class TestDefaultABIArgInfo(TestCase):
    '''Simply exercise the API
    '''
    def test_abi_int(self):
        tm = TargetMachine.new()
        td = tm.target_data.clone()
        abiinfo = DefaultABIInfo(td)
        abiinfo.compute_info(Type.void(), [Type.int(1), Type.int(8),
                                           Type.int(16), Type.int(32),
                                           Type.int(64)])
        print(abiinfo.arg_infos)
        print(abiinfo.return_info)

        abiinfo.compute_info(Type.int(32), [])
        print(abiinfo.arg_infos)
        print(abiinfo.return_info)

tests.append(TestDefaultABIArgInfo)

if __name__ == '__main__':
    unittest.main()
