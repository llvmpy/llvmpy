#! /usr/bin/env python
# ______________________________________________________________________

from __future__ import absolute_import

import sys
import unittest

from llpython import byte_control

# ______________________________________________________________________
# Global data

# Technically we could also compute if we need special logic for the
# old bytecode compiler by scanning for JUMP_IF_TRUE and JUMP_IF_FALSE
# opcodes.  These opcodes require additional POP_TOP's be inserted.
OLD_BYTECODE_COMPILER = sys.version_info < (2, 7)

got_done = 0

# ______________________________________________________________________
# Utility function definitions

def do_something():
    global got_done
    got_done += 1
    print("Something good got done.")
    return got_done

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

# ____________________________________________________________

def try_finally_2(m, n): # why == WHY_CONTINUE
    i = m
    while i < n:
        try:
            if i == 101:
                i += 200
                continue
        finally:
            do_something()
        i += 1
    return i

# ____________________________________________________________

def try_finally_3(m, n): # why == WHY_EXCEPTION (or WHY_RETURN)
    d = {}
    try:
        return d[n] - d[m]
    finally:
        do_something()
    return do_something_else()

# ____________________________________________________________

def try_finally_4(m, n): # why == WHY_NOT
    try:
        rv = n - m
    finally:
        do_something()
    return rv

# ____________________________________________________________

def try_finally_5(m, n):
    for i in range(m, n):
        try:
            if i == 99:
                break
            elif i == 121:
                continue
            elif i == 86:
                return
            elif i < -102:
                raise ValueError(i)
            else:
                try:
                    if i < 0:
                        raise ValueError(i)
                finally:
                    do_something()
        finally:
            do_something()
    return do_something()

# ______________________________________________________________________
# Class (test case) definition(s)

class TestByteControl(unittest.TestCase):
    def fail_unless_cfg_match(self, test_cfg, block_count, edges):
        assert len(test_cfg.blocks) == block_count
        block_keys = list(test_cfg.blocks.keys())
        block_keys.sort()
        expected_blocks_in = dict((block_key, set())
                                  for block_key in block_keys)
        expected_blocks_out = dict((block_key, set())
                                   for block_key in block_keys)
        for from_block_ofs, to_block_ofs in edges:
            from_block = block_keys[from_block_ofs]
            to_block = block_keys[to_block_ofs]
            expected_blocks_in[to_block].add(from_block)
            expected_blocks_out[from_block].add(to_block)
        for block_key in block_keys:
            expected_in = expected_blocks_in[block_key]
            test_in = test_cfg.blocks_in[block_key]
            self.assertEqual(
                expected_in, test_in, '%r != %r for blocks_in[%d]' % (
                    test_in, expected_in, block_key))
            expected_out = expected_blocks_out[block_key]
            test_out = test_cfg.blocks_out[block_key]
            self.assertEqual(
                expected_out, test_out, '%r != %r for set blocks_out[%d]' % (
                    test_out, expected_out, block_key))

    def test_raise(self):
        cfg = byte_control.build_cfg(do_something_else)
        self.fail_unless_cfg_match(cfg, 2, ())

    def test_try_finally_0(self):
        """
        Expected CFG (Python 2.7+):
        digraph CFG_try_finally_0 {
            BLOCK_0 -> BLOCK_3; // 0 -> 1
            BLOCK_0 -> BLOCK_15; // 0 -> 3
            BLOCK_3 -> BLOCK_15; // 1 -> 3
            // DEAD: BLOCK_11 -> BLOCK_15; // 2 -> 3
            BLOCK_15 -> BLOCK_23; // 3 -> 4, why == WHY_NOT
            BLOCK_23; // 4
        }
        (Possibly terminal blocks: 15, 23.)
        """
        cfg = byte_control.build_cfg(try_finally_0)
        self.fail_unless_cfg_match(cfg, 5, ((0, 1), (0, 3), (1, 3),
                                            (3, 4)))

    def test_try_finally_1(self):
        """
        Expected CFG (Python 2.7+):
        digraph CFG_try_finally_1 {
            BLOCK_0 -> BLOCK_9; // 0 -> 1
            BLOCK_0 -> BLOCK_63; // 0 -> 11
            BLOCK_9 -> BLOCK_22; // 1 -> 2
            BLOCK_22 -> BLOCK_25; // 2 -> 3
            BLOCK_22 -> BLOCK_62; // 2 -> 10
            BLOCK_25 -> BLOCK_31; // 3 -> 4
            BLOCK_25 -> BLOCK_51; // 3 -> 8
            BLOCK_31 -> BLOCK_43; // 4 -> 5
            BLOCK_31 -> BLOCK_47; // 4 -> 7
            BLOCK_43 -> BLOCK_51; // 5 -> 8
            // DEAD: BLOCK_44 -> BLOCK_47; // 6 -> 7
            BLOCK_47 -> BLOCK_51; // 7 -> 8
            BLOCK_51 -> BLOCK_59; // 8 -> 9, why == WHY_NOT
            BLOCK_51 -> BLOCK_63; // 8 -> 11, why == WHY_BREAK, WHY_RETURN, ...
            BLOCK_59 -> BLOCK_22; // 9 -> 2
            BLOCK_62 -> BLOCK_63; // 10 -> 11
            BLOCK_63; // 11
        }
        (Possibly terminal blocks: 51, 63.)
        """
        cfg = byte_control.build_cfg(try_finally_1)
        if not OLD_BYTECODE_COMPILER:
            self.fail_unless_cfg_match(
                cfg, 12, ((0, 1), (0, 11), (1, 2), (2, 3), (2, 10), (3, 4),
                          (3, 8), (4, 5), (4, 7), (5, 8), (7, 8),
                          (8, 9), (8, 11), (9, 2), (10, 11)))
        else:
            self.fail_unless_cfg_match(
                cfg, 13, ((0, 1), (0, 12), (1, 2), (2, 3), (2, 11), (3, 4),
                          (3, 9), (4, 5), (4, 7), (5, 9), (7, 8),
                          (8, 9), (9, 10), (9, 12), (10, 2), (11, 12)))

    def test_try_finally_2(self):
        """
        Expected CFG (Python 2.7+):
        digraph CFG_try_finally_2 {
            BLOCK_0 -> BLOCK_9; // 0 -> 1
            BLOCK_0 -> BLOCK_78; // 0 -> 10
            BLOCK_9 -> BLOCK_21; // 1 -> 2
            BLOCK_9 -> BLOCK_77; // 1 -> 9
            BLOCK_21 -> BLOCK_24; // 2 -> 3
            BLOCK_21 -> BLOCK_56; // 2 -> 7
            BLOCK_24 -> BLOCK_36; // 3 -> 4
            BLOCK_24 -> BLOCK_52; // 3 -> 6
            BLOCK_36 -> BLOCK_56; // 4 -> 7
            // DEAD: BLOCK_49 -> BLOCK_52; // 5 -> 6
            BLOCK_52 -> BLOCK_56; // 6 -> 7
            BLOCK_56 -> BLOCK_9; // 7 -> 1, why == WHY_CONTINUE
            BLOCK_56 -> BLOCK_64; // 7 -> 8, why == WHY_NOT
            BLOCK_64 -> BLOCK_9; // 8 -> 1
            BLOCK_77 -> BLOCK_78; // 9 -> 10
            BLOCK_78; // 10
        }
        (Possibly terminal blocks: 56, 78.)
        """
        cfg = byte_control.build_cfg(try_finally_2)
        if not OLD_BYTECODE_COMPILER:
            self.fail_unless_cfg_match(
                cfg, 11, ((0, 1), (0, 10), (1, 2), (1, 9), (2, 3), (2, 7),
                          (3, 4), (3, 6), (4, 7), (6, 7), (7, 1),
                          (7, 8), (8, 1), (9, 10)))

    def test_try_finally_3(self):
        """
        Expected (Python 2.7+):
        digraph CFG_foo3 {
            BLOCK_0 -> BLOCK_9; // 0 -> 1
            BLOCK_0 -> BLOCK_29; // 0 -> 3
            BLOCK_9 -> BLOCK_29; // 1 -> 3
            // DEAD: BLOCK_25 -> BLOCK_29; // 2 -> 3
            BLOCK_29 -> BLOCK_37; // 3 -> 4, why == WHY_NOT
            BLOCK_37; // 4
        }
        (Possibly terminal blocks: 29, 37.)
        """
        cfg = byte_control.build_cfg(try_finally_3)
        self.fail_unless_cfg_match(cfg, 5, ((0, 1), (0, 3), (1, 3),
                                            (3, 4)))

    def test_try_finally_4(self):
        """
        Expected:
        digraph CFG_foo4 {
           BLOCK_0 -> BLOCK_3; // 0 -> 1
           BLOCK_0 -> BLOCK_17; // 0 -> 2
           BLOCK_3 -> BLOCK_17; // 1 -> 2
           BLOCK_17 -> BLOCK_25; // 2 -> 3, why == WHY_NOT
           BLOCK_25; // 3
        }
        (Possibly terminal blocks: 17, 25.)
        """
        cfg = byte_control.build_cfg(try_finally_4)
        self.fail_unless_cfg_match(cfg, 4, ((0, 1), (0, 2), (1, 2), (2, 3)))

    def test_try_finally_5(self):
        cfg = byte_control.build_cfg(try_finally_5)
        if not OLD_BYTECODE_COMPILER:
            self.fail_unless_cfg_match(
                cfg, 26, ((0, 1), (0, 25), (1, 2), (2, 24), (2, 3), (3, 4),
                          (3, 22), (4, 5), (4, 7), (5, 22), (7, 8),
                          (7, 10), (8, 22), (10, 11), (10, 12),
                          (11, 22), (12, 13), (12, 15), (13, 22),
                          (15, 16), (15, 20), (16, 17), (16, 19), (17, 20),
                          (19, 20), (20, 21), (20, 22), (21, 22),
                          (22, 25), (22, 2), (22, 23), (23, 2), (24, 25)))

# ______________________________________________________________________

if __name__ == "__main__":
    unittest.main()

# ______________________________________________________________________
# End of test_byte_control.py
