#!/usr/bin/env python

from llvm.core import *

## create a module
module = Module.new("my_module")

## create a function type taking two doubles and returning a (32-bit) integer
ty_double = Type.double()
ty_int    = Type.int()
ty_func   = Type.function( ty_int, [ ty_double, ty_double ] )

## create a function of this type
func      = Function.new( module, ty_func, "foobar" )

# name function args
func.args[0].name = "arg1"
func.args[1].name = "arg2"

## implement the function

# add a basic block
entry = func.append_basic_block("entry")

# create an llvm::IRBuilder
builder = Builder.new()
builder.position_at_end(entry)

# add two args into temp1
temp1 = builder.add(func.args[0], func.args[1], "temp1")

# sub `1' from that
one = Constant.real( ty_double, 1.0 )
temp2 = builder.sub(temp1, one, "temp2")

# convert to integer
temp3 = builder.fptoui(temp2, ty_int, "temp3")

# return it
builder.ret(temp3)

# dump the module to see the bc
module.dump()
