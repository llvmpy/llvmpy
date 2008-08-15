#!/usr/bin/env python

# Import the llvm-py modules.
from llvm import *
from llvm.core import *

# Create an (empty) module.
my_module = Module.new('my_module')

# All the types involved here are "int"s. This type is represented
# by an object of the llvm.core.Type class:
ty_int = Type.int()   # by default 32 bits

# We need to represent the class of functions that accept two integers
# and return an integer. This is represented by an object of the
# function type (llvm.core.FunctionType):
ty_func = Type.function(ty_int, [ty_int, ty_int])

# Now we need a function named 'sum' of this type. Functions are not
# free-standing (in llvm-py); it needs to be contained in a module.
f_sum = my_module.add_function(ty_func, "sum")

# Let's name the function arguments as 'a' and 'b'.
f_sum.args[0].name = "a"
f_sum.args[1].name = "b"

# Our function needs a "basic block" -- a set of instructions that
# end with a terminator (like return, branch etc.). By convention
# the first block is called "entry".
bb = f_sum.append_basic_block("entry")

# Let's add instructions into the block. For this, we need an
# instruction builder:
builder = Builder.new(bb)

# OK, now for the instructions themselves. We'll create an add
# instruction that returns the sum as a value, which we'll use
# a ret instruction to return.
tmp = builder.add(f_sum.args[0], f_sum.args[1], "tmp")
builder.ret(tmp)

# We've completed the definition now! Let's see the LLVM assembly
# language representation of what we've created:
print my_module

