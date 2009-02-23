#!/usr/bin/env python

# Tests accessing of instruction operands.

from llvm.core import *

#===----------------------------------------------------------------------===

# implement a test function
def make_function():
    test_module = """
    define i32 @prod(i32, i32) {
    entry:
            %2 = mul i32 %0, %1
            ret i32 %2
    }

    define i32 @test_func(i32, i32, i32) {
    entry:
            %tmp1 = call i32 @prod(i32 %0, i32 %1)
            %tmp2 = add i32 %tmp1, %2
            %tmp3 = add i32 %tmp2, 1
            ret i32 %tmp3
    }
    """
    class strstream(object):
        def __init__(self): pass
        def read(self): return test_module
    m = Module.from_assembly(strstream())
    print "-"*60
    print m
    print "-"*60
    print "Examining function `test_func':"
    return m.get_function_named("test_func")

#===----------------------------------------------------------------------===

func = make_function()
idx = 1
for inst in func.basic_blocks[0].instructions:
    print "Instruction #%d:" % (idx,)
    print "  operand_count =", inst.operand_count
    print "  operands:"
    oidx = 1
    for op in inst.operands:
        print "    %d: %s" % (oidx, repr(op))
        oidx += 1
    idx += 1
