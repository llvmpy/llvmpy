#!/usr/bin/env python

# watch out for uncollected objects
import gc

import unittest, sys

from llvm import *
from llvm.core import *

class TestModule(unittest.TestCase):

    def setUp(self):
        pass

    def testmodule_and_moduleprovider(self):
        """Ownership issues between Module and ModuleProvider objects."""

        def temp_mp(m):
            mp = ModuleProvider.new(m)
            del mp

        def temp_m():
            m = Module.new("temp_m")
            return ModuleProvider.new(m)

        # check basic ownership and deletion
        m = Module.new("test1.1")
        self.assertEqual(m.owner, None)
        mp = ModuleProvider.new(m)
        self.assertEqual(m.owner, mp)
        mp_repr = repr(mp)
        mp = None
        self.assertNotEqual(m.owner, None)
        self.assertEqual(repr(m.owner), mp_repr)
        m = None
        self.assertEqual(gc.garbage, [])

        # delete a module which was owned by a module provider that has
        # gone out of scope
        m2 = Module.new("test1.2")
        temp_mp(m2)
        del m2
        self.assertEqual(gc.garbage, [])

        # delete a module provider object which owned a module that has
        # gone out of scope
        mp3 = temp_m()
        mp3 = None

        # check ref counts
        m4 = Module.new("test1.4")
        self.assertEqual(sys.getrefcount(m4), 1+1)
        mp4 = ModuleProvider.new(m4)
        self.assertEqual(sys.getrefcount(m4), 1+1)
        self.assertEqual(sys.getrefcount(mp4), 2+1)
        m4 = None
        self.assertEqual(sys.getrefcount(mp4), 1+1)
        mp4 = None

        # cannot create a second module provider object for the same
        # module
        works = False
        m5 = Module.new("test1.5")
        mp5 = ModuleProvider.new(m5)
        try:
            mp5_2 = ModuleProvider.new(m5)
        except LLVMException:
            works = True
        self.assertEqual(works, True)


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
        reqd = "; ModuleID = 'test4.1'\n\t%typename41 = type i32\n"
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
