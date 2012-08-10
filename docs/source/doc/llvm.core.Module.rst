+-----------------------------+
| layout: page                |
+-----------------------------+
| title: Module (llvm.core)   |
+-----------------------------+

Modules are top-level container objects. You need to create a module
object first, before you can add global variables, aliases or functions.
Modules are created using the static method ``Module.new``:


.. code-block:: python

   #!/usr/bin/env python
   
   from llvm import \* from llvm.core import \*
   
   # create a module
   my_module = Module.new('my_module')
