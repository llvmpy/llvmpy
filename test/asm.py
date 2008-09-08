#!/usr/bin/env python

from llvm import *
from llvm.core import *

# create a module
m = Module.new('module1')
m.add_global_variable(Type.int(), 'i')

# write it's assembly representation to a file
asm = str(m)
print >> file("/tmp/testasm.ll", "w"), asm

# read it back into a module
m2 = Module.from_assembly(file("/tmp/testasm.ll"))
print m2

