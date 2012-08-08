---
layout: page
title: FunctionType (llvm.core)
---

# llvm.core.FunctionType

## Base Class

- [llvm.core.Type](llvm.core.Type.html)

## Properties

### `return_type`


\[read-only\]

A [Type][llvm.core.Type] object, representing the return type of the function.

### `vararg`


\[read-only\]

`True` if the function is variadic.

### `args`


\[read-only\]

Returns an iterable object that yields [Type][llvm.core.Type] objects that
represent, in order, the types of the arguments accepted by the
function. Used like this:

{% highlight python %}
func_type = Type.function( Type.int(), [ Type.int(), Type.int() ] )
for arg in func_type.args:
    assert arg.kind == TYPE_INTEGER
    assert arg == Type.int()
assert func_type.arg_count == len(func_type.args)
{% endhighlight %}


### `arg_count`


\[read-only\]

The number of arguments. Same as `len(obj.args)`, but faster.

[llvm.core.Type]: llvm.core.Type.html
