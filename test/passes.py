#!/usr/bin/env python

from llvm.core import *
from llvm.passes import *
from llvm.ee import *

# A helper class.
class strstream(object):
    def __init__(self, s):
        self.s = s
    def read(self):
        return self.s

# Create a module.
asm = """

define i32 @test() nounwind {
    ret i32 42
}

define i32 @test1() nounwind  {
entry:
	%tmp = alloca i32
	store i32 42, i32* %tmp, align 4
	%tmp1 = load i32* %tmp, align 4
	%tmp2 = call i32 @test()
	%tmp3 = load i32* %tmp, align 4
	%tmp4 = load i32* %tmp, align 4
    ret i32 %tmp1
}

define i32 @test2() nounwind  {
entry:
	%tmp = call i32 @test()
    ret i32 %tmp
}
"""
m = Module.from_assembly(strstream(asm))
mp = ModuleProvider.new(m)
print "-"*72
print m

# Let's run a module-level inlining pass. First, create a pass manager.
pm = PassManager.new()

# Add the target data as the first "pass". This is mandatory.
pm.add( TargetData.new('') )

# Add the inlining pass.
pm.add( PASS_FUNCTION_INLINING )

# Run it!
pm.run(m)

# Done with the pass manager.
del pm

# Print the result. Note the change in @test2.
print "-"*72
print m


# Let's run a DCE pass on the the function 'test1' now. First create a
# function pass manager.
fpm = FunctionPassManager.new(mp)

# Add the target data as first "pass". This is mandatory.
fpm.add( TargetData.new('') )

# Add a DCE pass
fpm.add( PASS_AGGRESSIVE_DCE )

# Run the pass on the function 'test1'
fpm.run( m.get_function_named('test1') )

# Print the result. Note the change in @test1.
print "-"*72
print m
