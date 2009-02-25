#!/usr/bin/env python

# Tests accessing of instruction operands.

from llvm.core import *

m = None

#===----------------------------------------------------------------------===

# implement a test function
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

test_func = m.get_function_named("test_func")
prod      = m.get_function_named("prod")

#===----------------------------------------------------------------------===
# test operands

print
i1 = test_func.basic_blocks[0].instructions[0]
i2 = test_func.basic_blocks[0].instructions[1]
print "Testing User.operand_count ..",
if i1.operand_count == 3 and i2.operand_count == 2:
    print "OK"
else:
    print "FAIL"

print "Testing User.operands ..",
c1 = i1.operands[0] is prod
c2 = i1.operands[1] is test_func.args[0]
c3 = i1.operands[2] is test_func.args[1]
c4 = i2.operands[0] is i1
c5 = i2.operands[1] is test_func.args[2]
c6 = len(i1.operands) == 3
c7 = len(i2.operands) == 2
if c1 and c2 and c3 and c5 and c6 and c7:
    print "OK"
else:
    print "FAIL"
print

#===----------------------------------------------------------------------===
# show test_function

print "Examining test_function `test_test_func':"
idx = 1
for inst in test_func.basic_blocks[0].instructions:
    print "Instruction #%d:" % (idx,)
    print "  operand_count =", inst.operand_count
    print "  operands:"
    oidx = 1
    for op in inst.operands:
        print "    %d: %s" % (oidx, repr(op))
        oidx += 1
    idx += 1
