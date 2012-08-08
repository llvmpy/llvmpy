---
layout: page
title: Values
---

[llvm.core.Value][] is the base class of all values computed by a program
that may be used as operands to other values. A value has a type
associated with it (an object of [llvm.core.Type][]).

The class hierarchy is:


    Value
      User
        Constant
          ConstantExpr
          ConstantAggregateZero
          ConstantInt
          ConstantFP
          ConstantArray
          ConstantStruct
          ConstantVector
          ConstantPointerNull
          UndefValue
          GlobalValue
            GlobalVariable
            Function
        Instruction
          CallOrInvokeInstruction
          PHINode
          SwitchInstruction
          CompareInstruction
      Argument
      BasicBlock


The [Value][llvm.core.Value] class is abstract, it's not meant to be
instantiated. [User][llvm.core.User] is a [Value][llvm.core.Value]
 that in turn uses (i.e., can refer to) other values (for
e.g., a constant expression 1+2 refers to two constant values 1 and 2).

[Constant][llvm.core.Constant]-s represent constants that appear within code or
as initializers of globals. They are constructed using static methods of
[Constant][llvm.core.Constant]. Various types of constants are represented by
various subclasses of [Constant][llvm.core.Constant].
However, most of them are empty and do not provide any additional attributes or methods over [Constant][llvm.core.Constant].

The [Function][functions] object represents an instance of a
function type. Such objects contain [Argument][llvm.core.Argument] objects,
which represent the actual,
local-variable-like arguments of the function (not to be confused with
the arguments returned by a function _type_ object -- these represent
the _type_ of the arguments).

The various [Instruction][llvm.core.Instruction]-s are created
by the [Builder][llvm.core.Builder] class. Most
instructions are represented by [Instruction][llvm.core.Instruction] itself,
but there are a few subclasses that represent interesting instructions.

[Value][llvm.core.Value] objects have a type (read-only),
and a name (read-write).

**Related Links**
[functions][],
[comparision][],
[llvm.core.Value][],
[llvm.core.User][],
[llvm.core.Constant][],
[llvm.core.GlobalValue][],
[llvm.core.GlobalVariable][],
[llvm.core.Argument][],
[llvm.core.Instruction][],
[llvm.core.Builder][],
[llvm.core.BasicBlock][]


[llvm.core.Type]: types.html
[functions]: functions.html
[comparision]: comparision.html
[llvm.core.Value]: llvm.core.Value.html
[llvm.core.User]: llvm.core.User.html
[llvm.core.Constant]: llvm.core.Constant.html
[llvm.core.GlobalValue]: llvm.core.GlobalValue.html
[llvm.core.GlobalVariable]: llvm.core.GlobalVariable.html
[llvm.core.Argument]: llvm.core.Argument.html
[llvm.core.Instruction]: llvm.core.Instruction.html
[llvm.core.Builder]: llvm.core.Builder.html
[llvm.core.BasicBlock]: llvm.core.BasicBlock.html
