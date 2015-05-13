#! /usr/bin/env python
# ______________________________________________________________________

from __future__ import absolute_import

import unittest

from llpython import addr_flow

from . import test_byte_flow

# ______________________________________________________________________
# Class (test case) definition(s)

class TestAddressFlowBuilder(unittest.TestCase, test_byte_flow.FlowTestMixin):
    BUILDER_CLS = addr_flow.AddressFlowBuilder

    def fail_unless_valid_instruction(self, instr):
        super(TestAddressFlowBuilder, self).fail_unless_valid_instruction(
            instr)
        for arg_addr in instr[-1]:
            self.fail_unless_valid_address(arg_addr)

# ______________________________________________________________________
# Main (unit test) routine

if __name__ == "__main__":
    unittest.main()

# ______________________________________________________________________
# End of test_addr_flow.py
