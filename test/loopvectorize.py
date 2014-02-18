from llvm.core import *
from llvm.passes import *
from llvm.ee import *
import llvm
from llvm.tests.support import TestCase
from os.path import dirname, join as join_path


import unittest
import re

class TestLoopVectorizer(TestCase):
    def test_loop_vectorizer(self):
        if llvm.version <= (3, 1):
            return # SKIP

        re_vector = re.compile("<\d+ x \w+>")

        tm = TargetMachine.new(opt=3)

        # Build passes
        pm = build_pass_managers(tm, opt=3, loop_vectorize=True, fpm=False).pm

        # Load test module
        asmfile = join_path(dirname(__file__), 'loopvectorize.ll')
        with open(asmfile) as asm:
            mod = Module.from_assembly(asm)

        before = str(mod)

        pm.run(mod)

        after = str(mod)
        self.assertNotEqual(after, before)

        before_vectors = re_vector.findall(before)
        self.assertFalse(before_vectors)
        after_vectors = re_vector.findall(after)
        self.assertLess(len(before_vectors), len(after_vectors))


if __name__ == '__main__':
    unittest.main()
