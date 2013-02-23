+-------------------------------------+
| layout: page                        |
+-------------------------------------+
| title: GlobalVariable (llvm.core)   |
+-------------------------------------+

llvm.core.GlobalVariable
========================

Global variables (``llvm.core.GlobalVariable``) are subclasses of
`llvm.core.GlobalValue <llvm.core.GlobalValue.html>`_ and represent
module-level variables. These can have optional initializers and can be
marked as constants. Global variables can be created either by using the
``add_global_variable`` method of the `Module <llvm.core.Module.html>`_
class, or by using the static method ``GlobalVariable.new``.


.. code-block:: python

   # create a global variable using
   add_global_variable method gv1 =
   module_obj.add_global_variable(Type.int(), "gv1")
   
   # or equivalently, using a static constructor method
   gv2 = GlobalVariable.new(module_obj, Type.int(), "gv2") {% endhighlight
   %}
   
   Existing global variables of a module can be accessed by name using
   ``module_obj.get_global_variable_named(name)`` or
   ``GlobalVariable.get``. All existing global variables can be enumerated
   via iterating over the property ``module_obj.global_variables``.
   
   {% highlight python %} # retrieve a reference to the global variable
   gv1, # using the get_global_variable_named method gv1 =
   module_obj.get_global_variable_named("gv1")
   
   # or equivalently, using the static ``get`` method:
   gv2 = GlobalVariable.get(module_obj, "gv2")
   
   # list all global variables in a module
   for gv in module_obj.global_variables: print gv.name, "of type",
   gv.type


Automatically Generated Documentation
-------------------------------------
.. autoclass:: llvm.core.GlobalVariable
   :members:
   :undoc-members:
