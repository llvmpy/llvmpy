+-------------------------+
| layout: page            |
+-------------------------+
| title: JIT Tutorial 2   |
+-------------------------+

{% highlight python %} #!/usr/bin/env python

from llvm.core import \*

create a module
===============

module = Module.new ("tut2")

create a function type taking 2 integers, return a 32-bit integer
=================================================================

ty\_int = Type.int (32) func\_type = Type.function (ty\_int, (ty\_int,
ty\_int))

create a function of that type
==============================

gcd = Function.new (module, func\_type, "gcd")

name function args
==================

x = gcd.args[0]; x.name = "x" y = gcd.args[1]; y.name = "y"

implement the function
======================

blocks...
=========

entry = gcd.append\_basic\_block ("entry") ret =
gcd.append\_basic\_block ("return") cond\_false =
gcd.append\_basic\_block ("cond\_false") cond\_true =
gcd.append\_basic\_block ("cond\_true") cond\_false\_2 =
gcd.append\_basic\_block ("cond\_false\_2")

create a llvm::IRBuilder
========================

bldr = Builder.new (entry) x\_eq\_y = bldr.icmp (IPRED\_EQ, x, y, "tmp")
bldr.cbranch (x\_eq\_y, ret, cond\_false)

bldr.position\_at\_end (ret) bldr.ret(x)

bldr.position\_at\_end (cond\_false) x\_lt\_y = bldr.icmp (IPRED\_ULT,
x, y, "tmp") bldr.cbranch (x\_lt\_y, cond\_true, cond\_false\_2)

bldr.position\_at\_end (cond\_true) y\_sub\_x = bldr.sub (y, x, "tmp")
recur\_1 = bldr.call (gcd, (x, y\_sub\_x,), "tmp") bldr.ret (recur\_1)

bldr.position\_at\_end (cond\_false\_2) x\_sub\_y = bldr.sub (x, y,
"x\_sub\_y") recur\_2 = bldr.call (gcd, (x\_sub\_y, y,), "tmp") bldr.ret
(recur\_2)

print(module) {% endhighlight %}
