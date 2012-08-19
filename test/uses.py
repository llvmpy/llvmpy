#!/usr/bin/env python

from llvm.core import *

import unittest, logging

class TestUses(unittest.TestCase):
    def test_uses(self):
        m = Module.new('a')
        t = Type.int()
        ft = Type.function(t, [t, t, t])
        f = m.add_function(ft, "func")
        b = f.append_basic_block('entry')
        bld = Builder.new(b)
        tmp1 = bld.add(Constant.int(t, 100), f.args[0], "tmp1")
        tmp2 = bld.add(tmp1, f.args[1], "tmp2")
        tmp3 = bld.add(tmp1, f.args[2], "tmp3")
        bld.ret(tmp3)

        logging.debug("-"*60)
        logging.debug(m)
        logging.debug("-"*60)

        logging.debug("Testing use count ..")
        self.assertEqual(f.args[0].use_count, 1)
        self.assertEqual(f.args[1].use_count, 1)
        self.assertEqual(f.args[2].use_count, 1)
        self.assertEqual(tmp1.use_count, 2)
        self.assertEqual(tmp2.use_count, 0)
        self.assertEqual(tmp3.use_count, 1)

        logging.debug("Testing uses ..")
        self.assert_(f.args[0].uses[0] is tmp1)
        self.assertEqual(len(f.args[0].uses), 1)
        self.assert_(f.args[1].uses[0] is tmp2)
        self.assertEqual(len(f.args[1].uses), 1)
        self.assert_(f.args[2].uses[0] is tmp3)
        self.assertEqual(len(f.args[2].uses), 1)
        self.assertEqual(len(tmp1.uses), 2)
        self.assertEqual(len(tmp2.uses), 0)
        self.assertEqual(len(tmp3.uses), 1)

if __name__ == '__main__':
    unittest.main()

