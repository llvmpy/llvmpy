---
layout: page
title: StructType (llvm.core)
---

# llvm.core.StructType

## Base Class

- [llvm.core.Type](llvm.core.Type.html)

## Methods

### `set_body(self, elems, packed=False)`

Define the body for opaque identified structure.

`elems` is an iterable of [llvm.core.Type](llvm.core.Type.html)
If `packed` is `True`, creates a packed structure.

## Properties

### `is_identified`
\[read-only\]

`True` if this is an identified structure.

### `is_literal`
\[read-only\]

`True` if this is a literal structure.

### `is_opaque`
\[read-only\]

`True` if this is an opaque structure.
Only identified structure can be opaque.

### `packed`
\[read-only\]

`True` if the structure is packed (no padding between elements).

### `name`

Use in identified structure.
If set to empty, the identified structure is removed from the global context.

### `elements`
\[read-only\]

Returns an iterable object that yields [Type](llvm.core.Type.html) objects that
represent, in order, the types of the elements of the structure.
Used like this:

{% highlight python %}
struct_type = Type.struct( [ Type.int(), Type.int() ] )
for elem in struct_type.elements:
    assert elem.kind == TYPE_INTEGER
    assert elem == Type.int()
assert struct_type.element_count == len(struct_type.elements)
{% endhighlight %}


### `element_count`
\[read-only\]

The number of elements. Same as `len(obj.elements)`, but faster.


