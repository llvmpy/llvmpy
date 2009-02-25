#!/usr/bin/env python

from llvm.core import *

# create a type handle object
th = TypeHandle.new(Type.opaque())

# create the struct with an opaque* instead of self*
ts = Type.struct([ Type.int(), Type.pointer(th.type) ])

# unify the types
th.type.refine(ts)

# create a module, and add a "typedef"
m = Module.new('mod1')
m.add_type_name("struct.node", th.type)

# show what we created
print m
