#! /usr/bin/env python
# ______________________________________________________________________

from __future__ import absolute_import

import unittest

from llpython import addr_flow, opcode_util

from . import test_byte_control as tbc

# ______________________________________________________________________
# Class (test case) definition(s)

class TestAddrFlow(unittest.TestCase):
    def fail_unless_valid_flow(self, flow):
        raise NotImplementedError("XXX")
        # TODO: Make sure child indices are valid bytecode addresses
        # TODO: Make sure opcode has a "reasonable" number of child indices

    def test_try_finally_0(self):
        self.fail_unless_valid_flow(
            addr_flow.build_addr_flow(tbc.try_finally_0))

    def test_try_finally_1(self):
        self.fail_unless_valid_flow(
            addr_flow.build_addr_flow(tbc.try_finally_1))

    def test_try_finally_2(self):
        self.fail_unless_valid_flow(
            addr_flow.build_addr_flow(tbc.try_finally_2))

    def test_try_finally_3(self):
        self.fail_unless_valid_flow(
            addr_flow.build_addr_flow(tbc.try_finally_3))

    def test_try_finally_4(self):
        self.fail_unless_valid_flow(
            addr_flow.build_addr_flow(tbc.try_finally_4))

    def test_try_finally_5(self):
        self.fail_unless_valid_flow(
            addr_flow.build_addr_flow(tbc.try_finally_5))

# ______________________________________________________________________
# Main (unit test) routine

if __name__ == "__main__":
    unittest.main()

# ______________________________________________________________________
# End of test_addr_flow.py
