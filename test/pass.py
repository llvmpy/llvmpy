from llvm.core import *
from llvm.passes import *
from llvm.ee import *
import llvm
import unittest

class TestPass(unittest.TestCase):
    def test_execerise_pass_api(self):
        # Test passes
        ps = Pass.new(PASS_DOT_DOM_ONLY)
        self.assertEqual(PASS_DOT_DOM_ONLY, ps.name)
        self.assertTrue(len(ps.description))

        ps = Pass.new(PASS_INLINE)
        self.assertEqual(PASS_INLINE, ps.name)
        self.assertTrue(len(ps.description))

        # Test target specific passes
        pm = PassManager.new()
        pm.add(ps)
        pm.add(TargetData.new("e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"))

        tm = TargetMachine.new()

        tli = TargetLibraryInfo.new(tm.triple)
        self.assertFalse(tli.name)
        self.assertTrue(tli.description)
        pm.add(tli)

        if llvm.version >= (3, 2) and llvm.version < (3, 3):
            tti = TargetTransformInfo.new(tm)
            self.assertFalse(tti.name)
            self.assertTrue(tti.description)

            pm.add(tti)

        pmb = PassManagerBuilder.new()
        pmb.opt_level = 3
        pmb.loop_vectorize = True

        pmb.populate(pm)



if __name__ == '__main__':
    unittest.main()

