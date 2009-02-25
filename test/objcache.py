#!/usr/bin/env python

from llvm.core import *

def check(a, b):
    if a is b:
        print "OK"
    else:
        print "FAIL"

def check_isnot(a, b):
    if not (a is b):
        print "OK"
    else:
        print "FAIL"

print "Testing module aliasing ..",
m1 = Module.new('a')
t = Type.int()
ft = Type.function(t, [t])
f1 = m1.add_function(ft, "func")
m2 = f1.module
check(m1, m2)

print "Testing global vairable aliasing 1 .. ",
gv1 = GlobalVariable.new(m1, t, "gv")
gv2 = GlobalVariable.get(m1, "gv")
check(gv1, gv2)

print "Testing global vairable aliasing 2 .. ",
gv3 = m1.global_variables[0]
check(gv1, gv3)

print "Testing global vairable aliasing 3 .. ",
gv2 = None
gv3 = None
gv1.delete()
gv4 = GlobalVariable.new(m1, t, "gv")
check_isnot(gv1, gv4)

print "Testing function aliasing 1 ..",
b1 = f1.append_basic_block('entry')
f2 = b1.function
check(f1, f2)

print "Testing function aliasing 2 ..",
f3 = m1.get_function_named("func")
check(f1, f3)

print "Testing function aliasing 3 ..",
f4 = Function.get_or_insert(m1, ft, "func")
check(f1, f4)

print "Testing function aliasing 4 ..",
f5 = Function.get(m1, "func")
check(f1, f5)

print "Testing function aliasing 5 ..",
f6 = m1.get_or_insert_function(ft, "func")
check(f1, f6)

print "Testing function aliasing 6 ..",
f7 = m1.functions[0]
check(f1, f7)

print "Testing argument aliasing .. ",
a1 = f1.args[0]
a2 = f1.args[0]
check(a1, a2)

print "Testing basic block aliasing 1 .. ",
b2 = f1.basic_blocks[0]
check(b1, b2)

print "Testing basic block aliasing 2 .. ",
b3 = f1.get_entry_basic_block()
check(b1, b3)

print "Testing basic block aliasing 3 .. ",
b31 = f1.entry_basic_block
check(b1, b31)

print "Testing basic block aliasing 4 .. ",
bldr = Builder.new(b1)
b4 = bldr.basic_block
check(b1, b4)

print "Testing basic block aliasing 5 .. ",
i1 = bldr.ret_void()
b5 = i1.basic_block
check(b1, b5)

print "Testing instruction aliasing 1 .. ",
i2 = b5.instructions[0]
check(i1, i2)

# phi node
phi = bldr.phi(t)
phi.add_incoming(f1.args[0], b1)
v2 = phi.get_incoming_value(0)
b6 = phi.get_incoming_block(0)

print "Testing PHI / basic block aliasing 5 .. ",
check(b1, b6)

print "Testing PHI / value aliasing .. ",
check(f1.args[0], v2)

