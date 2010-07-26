#!/usr/bin/env python

# watch out for uncollected objects
import gc

import unittest, sys

from llvm import *
from llvm.core import *

class TestModule(unittest.TestCase):

    def setUp(self):
        pass


    def testdata_layout(self):
        """Data layout property."""
        m = Module.new("test2.1")
        self.assertEqual(m.data_layout, '')
        m.data_layout = 'some_value'
        self.assertEqual(m.data_layout, 'some_value')
        reqd = '; ModuleID = \'test2.1\'\ntarget datalayout = "some_value"\n'
        self.assertEqual(str(m), reqd)


    def testtarget(self):
        """Target property."""
        m = Module.new("test3.1")
        self.assertEqual(m.target, '')
        m.target = 'some_value'
        self.assertEqual(m.target, 'some_value')
        reqd = '; ModuleID = \'test3.1\'\ntarget triple = "some_value"\n'
        self.assertEqual(str(m), reqd)


    def testtype_name(self):
        """Type names."""
        m = Module.new("test4.1")
        r = m.add_type_name("typename41", Type.int())
        self.assertEqual(r, 0)
        r = m.add_type_name("typename41", Type.int())
        self.assertEqual(r, 1)
        reqd = "; ModuleID = 'test4.1'\n\n%typename41 = type i32\n"
        self.assertEqual(str(m), reqd)
        r = m.delete_type_name("typename41")
        reqd = "; ModuleID = 'test4.1'\n"
        self.assertEqual(str(m), reqd)
        r = m.delete_type_name("no such name") # nothing should happen
        reqd = "; ModuleID = 'test4.1'\n"
        self.assertEqual(str(m), reqd)


    def testglobal_variable(self):
        """Global variables."""
        m = Module.new("test5.1")
        t = Type.int()
        gv = m.add_global_variable(t, "gv")
        self.assertNotEqual(gv, None)
        self.assertEqual(gv.name, "gv")
        self.assertEqual(gv.type, Type.pointer(t))


def main():
    gc.set_debug(gc.DEBUG_LEAK)

    # run tests
    unittest.main()

    # done
    if gc.garbage:
        print "garbage = ", gc.garbage


main()
