#!/usr/bin/env python

from llvm import *
from llvm.core import *

# LLVM
# module contains functions and globals
# functions contain basic blocks and arguments
# basic blocks contain instructions
# instructions contain opcodes and operands

# an example of alloca, load, and store
# translate the following C, foo.c, program into LLVM IR
# int foo()
# {
#     int a = 7;
#     int b = a + 6;
#     return b;
# }
#
# int main()
# {
#     int c = foo();
#     return 0;
# }
#
# the llvm IR to generate was found by compling foo.c as
# clang -emit-llvm -S foo.c 

# create a module
mod = Module.new('foo')

# todo create execution engine, an exercise for the reader

#create types
ty_int = Type.int(32)
func_type = Type.function(ty_int, tuple())

# define a constant 
ZERO = Constant.int(ty_int, 0)

#create a function that returns an int and takes no parameters
foo = Function.new(mod, func_type, "foo")
foo.calling_convention = CC_C

#implement body of function foo
blk = foo.append_basic_block("entry")

# implement IR
bldr = Builder.new(blk)
# alocate memory for a and b
a = bldr.alloca(ty_int, name='a')
b = bldr.alloca(ty_int, name='b')

# don't do this - bldr.store(7, a) - as 7 is a Python object
# and not a llvm,core.Constant object
# store 7 in a, a = 7
bldr.store(Constant.int(ty_int, 7), a)

# read the value of a and copy to register
# llvm IR is a RISC like machine - operands have to be in registers before you can add
load_a = bldr.load(a)
add = bldr.add(load_a, Constant.int(ty_int, 6), name='add')

# make the assignment, b = a + 6
bldr.store(add, b)

# read the value of b and copy to register
load_b = bldr.load(b)
bldr.ret(load_b)

# main has same function type as foo
main  = Function.new(mod, func_type, "main")
main.calling_convention = CC_C

# implement body of main
blk = main.append_basic_block("entry")

# implement IR
bldr = Builder.new(blk)

# IR
c = bldr.alloca(ty_int, name='c')
call = bldr.call(foo, tuple(), name='call')
bldr.store(call, c)
bldr.ret(ZERO)

# IR sans target info
print mod

with open('foo.ll', 'w') as f:
    f.write(mod.__str__())


