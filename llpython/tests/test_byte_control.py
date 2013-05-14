#! /usr/bin/env python
# ______________________________________________________________________

from __future__ import absolute_import

import unittest

from llpython import byte_control

# ______________________________________________________________________
# Global data

got_done = 0

# ______________________________________________________________________
# Utility function definitions

def do_something():
    global got_done
    got_done += 1
    print("Something good got done.")

# ____________________________________________________________

def do_something_else():
    raise Exception("Something bad got done, and I don't like it")

# ______________________________________________________________________
# Test function definitions

def try_finally_0(m, n): # why == WHY_RETURN
    try:
        return n - m
    finally:
        do_something()
    return do_something_else()

# ____________________________________________________________

def try_finally_1(m, n): # why == WHY_BREAK
    i = -1
    for i in range(m, n):
        try:
            if i == 101:
                break
        finally:
            do_something()
    return i

# ______________________________________________________________________
# Class (test case) definition(s)

class TestByteControl(unittest.TestCase):
    def fail_unless_cfg_match(self, test_cfg, block_count, edges):
        assert len(test_cfg.blocks) == block_count
        block_keys = list(test_cfg.blocks.keys())
        block_keys.sort()
        # TODO: Ensure unexpected edges cause error.
        for from_block_ofs, to_block_ofs in edges:
            from_block = block_keys[from_block_ofs]
            to_block = block_keys[to_block_ofs]
            assert from_block in test_cfg.blocks_in[to_block]
            assert to_block in test_cfg.blocks_out[from_block]

    def test_try_finally_0(self):
        cfg = byte_control.build_cfg(try_finally_0)
        self.fail_unless_cfg_match(cfg, 5, ((0, 1), (0, 3), (1, 3), (2, 3),
                                            (3, 4)))

    def test_try_finally_1(self):
        cfg = byte_control.build_cfg(try_finally_1)
        # TODO: Translate known graph to offsets...
        self.fail_unless_cfg_match(cfg, 12, ())

# ______________________________________________________________________

if __name__ == "__main__":
    unittest.main()

# ______________________________________________________________________
# End of test_byte_control.py
