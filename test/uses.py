#!/usr/bin/env python

from llvm.core import *

m = Module.new('a')
t = Type.int()
ft = Type.function(t, [t, t, t])
f = m.add_function(ft, "func")
b = f.append_basic_block('entry')
bld = Builder.new(b)
tmp1 = bld.add(Constant.int(t, 100), f.args[0], "tmp1")
tmp2 = bld.add(tmp1, f.args[1], "tmp2")
tmp3 = bld.add(tmp1, f.args[2], "tmp3")
bld.ret(tmp3)

print "-"*60
print m
print "-"*60

print "Testing use count ..",
c1 = f.args[0].use_count == 1
c2 = f.args[1].use_count == 1
c3 = f.args[2].use_count == 1
c4 = tmp1.use_count == 2
c5 = tmp2.use_count == 0
c6 = tmp3.use_count == 1
if c1 and c2 and c3 and c4 and c5 and c6:
    print "OK"
else:
    print "FAIL"

print "Testing uses ..",
c1 = f.args[0].uses[0] is tmp1
c2 = len(f.args[0].uses) == 1
c3 = f.args[1].uses[0] is tmp2
c4 = len(f.args[1].uses) == 1
c5 = f.args[2].uses[0] is tmp3
c6 = len(f.args[2].uses) == 1
c7 = len(tmp1.uses) == 2
c8 = len(tmp2.uses) == 0
c9 = len(tmp3.uses) == 1
if c1 and c2 and c3 and c4 and c5 and c6 and c7 and c8 and c9:
    print "OK"
else:
    print "FAIL"
