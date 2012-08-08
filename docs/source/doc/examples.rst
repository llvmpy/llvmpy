+--------------------------------------+
| layout: page                         |
+--------------------------------------+
| title: Examples and LLVM Tutorials   |
+--------------------------------------+

-  This will become a table of contents (this text will be scraped).
   {:toc}

Examples
========

A Simple Function
-----------------

Let's create a (LLVM) module containing a single function, corresponding
to the ``C`` function:

{% highlight c %} int sum(int a, int b) { return a + b; } {%
endhighlight %}

Here's how it looks like:

{% highlight python %} #!/usr/bin/env python

Import the llvm-py modules.
===========================

from llvm import \* from llvm.core import \*

Create an (empty) module.
=========================

my\_module = Module.new('my\_module')

All the types involved here are "int"s. This type is represented
================================================================

by an object of the llvm.core.Type class:
=========================================

ty\_int = Type.int() # by default 32 bits

We need to represent the class of functions that accept two integers
====================================================================

and return an integer. This is represented by an object of the
==============================================================

function type (llvm.core.FunctionType):
=======================================

ty\_func = Type.function(ty\_int, [ty\_int, ty\_int])

Now we need a function named 'sum' of this type. Functions are not
==================================================================

free-standing (in llvm-py); it needs to be contained in a module.
=================================================================

f\_sum = my\_module.add\_function(ty\_func, "sum")

Let's name the function arguments as 'a' and 'b'.
=================================================

f\_sum.args[0].name = "a" f\_sum.args[1].name = "b"

Our function needs a "basic block" -- a set of instructions that
================================================================

end with a terminator (like return, branch etc.). By convention
===============================================================

the first block is called "entry".
==================================

bb = f\_sum.append\_basic\_block("entry")

Let's add instructions into the block. For this, we need an
===========================================================

instruction builder:
====================

builder = Builder.new(bb)

OK, now for the instructions themselves. We'll create an add
============================================================

instruction that returns the sum as a value, which we'll use
============================================================

a ret instruction to return.
============================

tmp = builder.add(f\_sum.args[0], f\_sum.args[1], "tmp")
builder.ret(tmp)

We've completed the definition now! Let's see the LLVM assembly
===============================================================

language representation of what we've created:
==============================================

print my\_module {% endhighlight %}

Here is the output:

{% highlight llvm %} ; ModuleID = 'my\_module'

define i32 @sum(i32 %a, i32 %b) { entry: %tmp = add i32 %a, %b ;
[#uses=1] ret i32 %tmp } {% endhighlight %}

Adding JIT Compilation
----------------------

Let's compile this function in-memory and run it.

{% highlight python %} #!/usr/bin/env python

Import the llvm-py modules.
===========================

from llvm import \* from llvm.core import \* from llvm.ee import \* #
new import: ee = Execution Engine

Create a module, as in the previous example.
============================================

my\_module = Module.new('my\_module') ty\_int = Type.int() # by default
32 bits ty\_func = Type.function(ty\_int, [ty\_int, ty\_int]) f\_sum =
my\_module.add\_function(ty\_func, "sum") f\_sum.args[0].name = "a"
f\_sum.args[1].name = "b" bb = f\_sum.append\_basic\_block("entry")
builder = Builder.new(bb) tmp = builder.add(f\_sum.args[0],
f\_sum.args[1], "tmp") builder.ret(tmp)

Create an execution engine object. This will create a JIT compiler
==================================================================

on platforms that support it, or an interpreter otherwise.
==========================================================

ee = ExecutionEngine.new(my\_module)

The arguments needs to be passed as "GenericValue" objects.
===========================================================

arg1 = GenericValue.int(ty\_int, 100) arg2 = GenericValue.int(ty\_int,
42)

Now let's compile and run!
==========================

retval = ee.run\_function(f\_sum, [arg1, arg2])

The return value is also GenericValue. Let's print it.
======================================================

print "returned", retval.as\_int() {% endhighlight %}

And here's the output:

::

    returned 142

--------------

LLVM Tutorials
==============

Simple JIT Tutorials
--------------------

The following JIT tutorials were contributed by Sebastien Binet.

1. `A First Function <examples/JITTutorial1.html>`_
2. `A More Complicated Function <examples/JITTutorial2.html>`_

Kaleidoscope ## {#kaleidoscope}
-------------------------------

Implementing a Language with LLVM

The LLVM `Kaleidoscope <http://www.llvm.org/docs/tutorial/>`_ tutorial
has been ported to llvm-py by Max Shawabkeh.

1. `Tutorial Introduction and the
   Lexer <kaleidoscope/PythonLangImpl1.html>`_
2. `Implementing a Parser and AST <kaleidoscope/PythonLangImpl2.html>`_
3. `Implementing Code Generation to LLVM
   IR <kaleidoscope/PythonLangImpl3.html>`_
4. `Adding JIT and Optimizer
   Support <kaleidoscope/PythonLangImpl4.html>`_
5. `Extending the language: control
   flow <kaleidoscope/PythonLangImpl5.html>`_
6. `Extending the language: user-defined
   operators <kaleidoscope/PythonLangImpl6.html>`_
7. `Extending the language: mutable variables / SSA
   construction <kaleidoscope/PythonLangImpl7.html>`_
8. `Conclusion and other useful LLVM
   tidbits <kaleidoscope/PythonLangImpl8.html>`_

