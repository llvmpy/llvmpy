import unittest
from llvm.core import (Module, Type, Builder, Constant)
from llvm.passes import FunctionPassManager
from llvm.ee import ExecutionEngine
from .support import TestCase, tests

class TestIssue100(TestCase):
    def test_issue100(self):
        m = Module.new('a')

        pm = FunctionPassManager.new(m)

        ee = ExecutionEngine.new(m)

        pm.add(ee.target_data)

        ti = Type.int()
        tf = Type.function(ti, [])

        f = m.add_function(tf, "func1")

        bb = f.append_basic_block('entry')

        b = Builder.new(bb)

        b.ret(Constant.int(ti, 0))

        f.verify()

        pm.run(f)

        assert ee.run_function(f, []).as_int() == 0



tests.append(TestIssue100)

if __name__ == '__main__':
    unittest.main()

