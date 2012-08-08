+-------------------------+
| layout: page            |
+-------------------------+
| title: JIT Tutorial 1   |
+-------------------------+

{% highlight python %} #!/usr/bin/env python

from llvm.core import \*

create a module
===============

module = Module.new ("tut1")

create a function type taking 3 32-bit integers, return a 32-bit integer
========================================================================

ty\_int = Type.int (32) func\_type = Type.function (ty\_int,
(ty\_int,)\*3)

create a function of that type
==============================

mul\_add = Function.new (module, func\_type, "mul\_add")
mul\_add.calling\_convention = CC\_C x = mul\_add.args[0]; x.name = "x"
y = mul\_add.args[1]; y.name = "y" z = mul\_add.args[2]; z.name = "z"

implement the function
======================

new block
=========

blk = mul\_add.append\_basic\_block ("entry")

IR builder
==========

bldr = Builder.new (blk) tmp\_1 = bldr.mul (x, y, "tmp\_1") tmp\_2 =
bldr.add (tmp\_1, z, "tmp\_2")

bldr.ret (tmp\_2)

print(module) {% endhighlight %}
