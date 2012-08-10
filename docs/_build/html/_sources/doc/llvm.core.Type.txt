+---------------------------+
| layout: page              |
+---------------------------+
| title: Type (llvm.core)   |
+---------------------------+

llvm.core.Type
==============

-  This will become a table of contents (this text will be scraped).
   {:toc}

Static Constructors
-------------------

``int(n)``
~~~~~~~~~~

Create an integer type of bit width ``n``.

``float()``
~~~~~~~~~~~

Create a 32-bit floating point type.

``double()``
~~~~~~~~~~~~

Create a 64-bit floating point type.

``x86_fp80()``
~~~~~~~~~~~~~~

Create a 80-bit 80x87-style floating point type.

``fp128()``
~~~~~~~~~~~

Create a 128-bit floating point type (112-bit mantissa).

``ppc_fp128()``
~~~~~~~~~~~~~~~

Create a 128-bit float (two 64-bits).

``function(ret, params, vararg=False)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a function type, having the return type ``ret`` (must be a
``Type``), accepting the parameters ``params``, where ``params`` is an
iterable, that yields ``Type`` objects representing the type of each
function argument in order. If ``vararg`` is ``True``, function is
variadic.

``struct(eltys, name='')``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create an unpacked structure. ``eltys`` is an iterable, that yields
``Type`` objects representing the type of each element in order.

If ``name`` is evaulates ``True`` (not empty), create an *identified
structure*; otherwise, create a *literal structure* by default.

``packed_struct(eltys, name='')``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like ``struct(eltys)``, but creates a packed struct.

``array(elty, count)``
~~~~~~~~~~~~~~~~~~~~~~

Creates an array type, holding ``count`` elements, each of type ``elty``
(which should be a ``Type``).

``pointer(pty, addrspc=0)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a pointer to type ``pty`` (which should be a ``Type``).
``addrspc`` is an integer that represents the address space of the
pointer (see LLVM docs or ask on llvm-dev for more info).

``void()``
~~~~~~~~~~

Creates a void type. Used for function return types.

``label()``
~~~~~~~~~~~

Creates a label type.

``opaque(name)``
~~~~~~~~~~~~~~~~

Opaque `StructType <llvm.core.StructType.html>`_, used for creating
self-referencing types.

Properties
----------

``kind``
~~~~~~~~

[read-only]

A value (enum) representing the "type" of the object. It will be one of
the following constants defined in ``llvm.core``:


.. code-block:: python

   # Warning: do not rely on actual numerical
   values! TYPE_VOID = 0 TYPE_FLOAT = 1 TYPE_DOUBLE = 2 TYPE_X86_FP80
   = 3 TYPE_FP128 = 4 TYPE_PPC_FP128 = 5 TYPE_LABEL = 6 TYPE_INTEGER =
   7 TYPE_FUNCTION = 8 TYPE_STRUCT = 9 TYPE_ARRAY = 10 TYPE_POINTER =
   11 TYPE_OPAQUE = 12 TYPE_VECTOR = 13 TYPE_METADATA = 14 TYPE_UNION =
   15



Example:
^^^^^^^^


.. code-block:: python

   assert Type.int().kind == TYPE_INTEGER assert
   Type.void().kind == TYPE_VOID
