#! /usr/bin/env python
# ______________________________________________________________________

from __future__ import absolute_import

import unittest

from llpython import byte_flow
from llpython import opcode_util

from . import test_byte_control as tbc
from . import llfuncs

# ______________________________________________________________________
# Class (test case) definition(s)

class FlowTestMixin(object):

    def fail_unless_valid_address(self, address):
        self.failUnless(address >= 0)
        self.failUnless(address < self.max_addr)
        self.failUnless(address in self.valid_addrs)

    def fail_unless_valid_instruction(self, instr):
        address = instr[0]
        self.visited.add(address)
        self.fail_unless_valid_address(instr[0])

    def fail_unless_valid_flow(self, flow, func):
        self.failUnless(len(flow) > 0)
        func_code = opcode_util.get_code_object(func).co_code
        self.valid_addrs = set(addr for addr, _, _ in
                               opcode_util.itercode(func_code))
        self.visited = set()
        self.max_addr = len(func_code)
        for block_index, block_instrs in flow.items():
            self.failUnless(block_index < self.max_addr)
            for instr in block_instrs:
                self.fail_unless_valid_instruction(instr)
        del self.max_addr
        # Make sure that all instructions identified by itercode were
        # checked at least once; they should be represented in the
        # resulting flow, even if their basic block is unreachable.
        self.failUnless(self.valid_addrs == self.visited,
                        'Failed to visit following addresses: %r' %
                        (self.valid_addrs - self.visited))
        del self.visited
        del self.valid_addrs
        return flow

    def build_and_test_flow(self, func):
        return self.fail_unless_valid_flow(
            self.BUILDER_CLS.build_flow(func), func)

    def test_doslice(self):
        self.build_and_test_flow(llfuncs.doslice)

    def test_ipow(self):
        self.build_and_test_flow(llfuncs.ipow)

    def test_pymod(self):
        self.build_and_test_flow(llfuncs.pymod)

    def test_try_finally_0(self):
        self.build_and_test_flow(tbc.try_finally_0)

    def test_try_finally_1(self):
        self.build_and_test_flow(tbc.try_finally_1)

    def test_try_finally_2(self):
        self.build_and_test_flow(tbc.try_finally_2)

    def test_try_finally_3(self):
        self.build_and_test_flow(tbc.try_finally_3)

    def test_try_finally_4(self):
        self.build_and_test_flow(tbc.try_finally_4)

    def test_try_finally_5(self):
        self.build_and_test_flow(tbc.try_finally_5)

# ______________________________________________________________________

class TestBytecodeFlowBuilder(unittest.TestCase, FlowTestMixin):

    BUILDER_CLS = byte_flow.BytecodeFlowBuilder

    def fail_unless_valid_instruction(self, instr):
        super(TestBytecodeFlowBuilder, self).fail_unless_valid_instruction(
            instr)
        for child_instr in instr[-1]:
            self.fail_unless_valid_instruction(child_instr)

# ______________________________________________________________________
# Main (unit test) routine

if __name__ == "__main__":
    unittest.main()

# ______________________________________________________________________
# End of test_byte_flow.py
