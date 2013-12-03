#!/usr/bin/env python

# watch out for uncollected objects
import gc

import unittest, sys, logging

from llvm import *
from llvm.core import *
from llvm.tests.support import TestCase

class TestModule(TestCase):

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

    # Type system is rewritten in LLVM 3.0.
    # Only named StructType is supported.
    # See http://blog.llvm.org/2011/11/llvm-30-type-system-rewrite.html
    #
    #    def testtype_name(self):
    #        """Type names."""
    #        m = Module.new("test4.1")
    #        r = m.add_type_name("typename41", Type.int())
    #        self.assertEqual(r, 0)
    #        r = m.add_type_name("typename41", Type.int())
    #        self.assertEqual(r, 1)
    #        reqd = "; ModuleID = 'test4.1'\n\n%typename41 = type i32\n"
    #        self.assertEqual(str(m), reqd)
    #        r = m.delete_type_name("typename41")
    #        reqd = "; ModuleID = 'test4.1'\n"
    #        self.assertEqual(str(m), reqd)
    #        r = m.delete_type_name("no such name") # nothing should happen
    #        reqd = "; ModuleID = 'test4.1'\n"
    #        self.assertEqual(str(m), reqd)

    def testtype_name(self):
        m = Module.new("test4.1")
        struct = Type.struct([Type.int(), Type.int()], name="struct.two.int")
        self.assertEqual(struct.name, "struct.two.int")
        got_struct = m.get_type_named(struct.name)
        self.assertEqual(got_struct.name, struct.name)

        self.assertEqual(got_struct.element_count, struct.element_count)
        self.assertEqual(len(struct.elements), struct.element_count)

        self.assertEqual(struct.elements, got_struct.elements)
        for elty in struct.elements:
            self.assertEqual(elty, Type.int())

        # rename identified type
        struct.name = 'new_name'
        self.assertEqual(struct.name, 'new_name')
        self.assertIs(m.get_type_named("struct.two.int"), None)

        self.assertEqual(got_struct.name, struct.name)

        # remove identified type
        struct.name = ''

        self.assertIs(m.get_type_named("struct.two.int"), None)
        self.assertIs(m.get_type_named("new_name"), None)

        # another name

        struct.name = 'another.name'
        self.assertEqual(struct.name, 'another.name')
        self.assertEqual(got_struct.name, struct.name)

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
    if sys.version_info[:2] > (2, 6):
        unittest.main(exit=False)  # set exit to False so that it will return.
    else:
        unittest.main()
    # done
    for it in gc.garbage:
        logging.debug('garbage = %s', it)

if __name__ == '__main__':
    main()



