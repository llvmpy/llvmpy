---
layout: page
title: Types
---

Types are what you think they are. A instance of [llvm.core.Type][], or
one of its derived classes, represent a type. llvm-py does not use as
many classes to represent types as does LLVM itself. Some types are
represented using [llvm.core.Type][] itself and the rest are represented
using derived classes of [llvm.core.Type][]. As usual, an instance is created
via one of the static methods of [Type][llvm.core.Type]. These methods return an
instance of either [llvm.core.Type][] itself or one of its derived
classes.

The following table lists all the available types along with the static
method which has to be used to construct it and the name of the class whose
object is actually returned by the static method.


Name | Constructor Method | Class |
-----|:------------------:|:-----:|
integer of bitwidth *n* | Type.int(n) | [IntegerType][llvm.core.IntegerType] |
32-bit float | Type.float() | [Type][llvm.core.Type] |
64-bit double | Type.double() | [Type][llvm.core.Type] |
80-bit float | Type.x86_fp80() | [Type][llvm.core.Type] |
128-bit float (112-bit mantissa) | Type.fp128() | [Type][llvm.core.Type] |
128-bit float (two 64-bits) | Type.ppc_fp128() | [Type][llvm.core.Type] |
function | Type.function(r, p, v) | [FunctionType][llvm.core.FunctionType] |
unpacked struct | Type.struct(eltys, name) | [StructType][llvm.core.StructType] |
packed struct | Type.packed_struct(eltys, name) | [StructType][llvm.core.StructType] |
opaque struct | Type.opaque(name) | [StructType][llvm.core.StructType] |
array | Type.array(elty, count) | [ArrayType][llvm.core.ArrayType] |
pointer to value of type *pty* | Type.pointer(pty, addrspc) | [PointerType][llvm.core.PointerType] |
vector | Type.vector(elty, count) | [VectorType][llvm.core.VectorType] |
void | Type.void() | [Type][llvm.core.Type] |
label | Type.label() | [Type][llvm.core.Type] |


<br/>


The class hierarchy is:


    Type
        IntegerType
        FunctionType
        StructType
        ArrayType
        PointerType
        VectorType



* * *

## An Example

Here is an example that demonstrates the creation of types:

{% highlight python %}
#!/usr/bin/env python

# integers
int_ty      = Type.int()
bool_ty     = Type.int(1)
int_64bit   = Type.int(64)

# floats
sprec_real  = Type.float()
dprec_real  = Type.double()

# arrays and vectors
intar_ty    = Type.array( int_ty, 10 )     # "typedef int intar_ty[10];"
twodim      = Type.array( intar_ty , 10 )  # "typedef int twodim[10][10];"
vec         = Type.array( int_ty, 10 )

# structures
s1_ty       = Type.struct( [ int_ty, sprec_real ] )
    # "struct s1_ty { int v1; float v2; };"

# pointers
intptr_ty   = Type.pointer(int_ty)         # "typedef int *intptr_ty;"

# functions
f1 = Type.function( int_ty, [ int_ty ] )
    # functions that take 1 int_ty and return 1 int_ty

f2 = Type.function( Type.void(), [ int_ty, int_ty ] )
    # functions that take 2 int_tys and return nothing

f3 = Type.function( Type.void(), ( int_ty, int_ty ) )
    # same as f2; any iterable can be used

fnargs = [ Type.pointer( Type.int(8) ) ]
printf = Type.function( Type.int(), fnargs, True ) # variadic function
{% endhighlight %}

* * *

## Another Example: Recursive Type

The type system was rewritten in LLVM 3.0.
The old opaque type was removed.
Instead, identified `StructType` can now be defined without a body.
Doing so creates a opaque structure.
One can then set the body after the construction of a structure.


(See [LLVM Blog](http://blog.llvm.org/2011/11/llvm-30-type-system-rewrite.html)
for detail about the new type system.)

The following code defines a opaque structure, named "mystruct".
The body is defined after the construction using `StructType.set_body`.
The second subtype is a pointer to a "mystruct" type.

{% highlight python %}
ts = Type.opaque('mystruct')
ts.set_body([Type.int(), Type.pointer(ts)])
{% endhighlight %}

* * *

**Related Links**
[llvm.core.Type][],
[llvm.core.IntegerType][],
[llvm.core.FunctionType][],
[llvm.core.StructType][],
[llvm.core.ArrayType][],
[llvm.core.PointerType][],
[llvm.core.VectorType][],
[llvm.core.TypeHandle][]





[llvm.core.Type]: llvm.core.Type.html
[llvm.core.IntegerType]: llvm.core.IntegerType.html
[llvm.core.FunctionType]: llvm.core.FunctionType.html
[llvm.core.StructType]: llvm.core.StructType.html
[llvm.core.ArrayType]: llvm.core.ArrayType.html
[llvm.core.PointerType]: llvm.core.PointerType.html
[llvm.core.VectorType]: llvm.core.VectorType.html
[llvm.core.TypeHandle]: llvm.core.TypeHandle.html

