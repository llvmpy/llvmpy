# README

This is a reimplementation of the LLVM binding, aiming to provide a more 
familiar interface to the C++ API whenever possible.

The implementation uses a custom DSL in python to describe the interface. 
The DSL serves as input to *gen/gen.py* for generation of the .cpp and .py files 
for the actual binding.

# How to Add New Class

Let's use the `llvm::Module` as an example because it should be one of the most
familiar class in LLVM.

Reference code in https://github.com/llvmpy/llvmpy/blob/master/llvmpy/src/Module.py
and see LLVM documentation at http://llvm.org/docs/doxygen/html/classllvm_1_1Module.html

1) Import binding helpers

```python
from binding import *
# Yes, it is bad practice to import star.
# I will fix it one day.
```

2) Import LLVM namespace

```python
from .namespace import llvm
```

3) Declare the class

```python
Module = llvm.Class()
```

4) Import all the dependencies for the definition

5) Define the class

```python
@Module
class Module:
    ...
```

## Inside the definition...

5.1) Use the ``_include_`` attribute to add include files.

5.2) Use ``Enum`` to create an enumerator type.

5.3) Make constructor 

Not every class needs to have a binding for the constructor.
Only add things that will be used.

```python
new = Constructor(cast(str, StringRef), ref(LLVMContext))
```

The constructor must be named as "new".

The args to ``Constructor`` are parameters of the signature.
The first parameter means cast Python string to a StringRef.
The second parameter means pass LLVMContext object as a value reference.

5.4) Make destructor

Not every class needs to have a binding for the destructor.
Only add things that will be used.
If it is always owned by another object, it usually does not need to have one.

```python
delete = Destructor()
```

The destructor must be named as "delete".

5.5) Add Simple Methods

```python
getFunction = Method(ptr(Function), cast(str, StringRef))
```

The first arg is the return type: a ponter to Function.
The rest of the args are for the parameters.

Note: ``cast(fromtype, totype)`` can be used as return-type as well.
In that case, the ``fromtype`` will usually refer to a LLVM object
and the ``totype`` will refer to the Python object.

5.6) Add custom methods defined in C++

The ``list_functions`` is created as a ``CustomMethod``.

```python
list_functions = CustomMethod('Module_list_functions', PyObjectPtr)
```

The first arg is the name that appears in C++.
The second argument is the return-type.
The rest of the arguments are parameters.

The definition of ``Module_list_functions`` is located in 
"include/llvm_binding/extra.h".

5.7) Add custom python method

One can also add custom methods in Python, e.g. ``__str__``.

```python
@CustomPythonMethod
def __str__(self):
    from llvmpy import extra
    os = extra.make_raw_ostream_for_printing()
    self.print_(os, None)
    return os.str()
```

The body of ``__str__`` is directly copied to the Python output file.
Thus, it can't reference to anything in current file scope.

# Static Methods

``StaticMethod`` https://github.com/llvmpy/llvmpy/blob/master/llvmpy/src/PassRegistry.py

``CustomStaticMethod`` https://github.com/llvmpy/llvmpy/blob/master/llvmpy/src/Support/TargetRegistry.py


# Namespace

``Namespace`` https://github.com/llvmpy/llvmpy/blob/master/llvmpy/src/Support/CodeGen.py

# Functions

``Function`` https://github.com/llvmpy/llvmpy/blob/master/llvmpy/src/Assembly/Parser.py

``CustomFunction`` https://github.com/llvmpy/llvmpy/blob/master/llvmpy/src/Bitcode/ReaderWriter.py





# Other Things from the binding.py

https://github.com/llvmpy/llvmpy/blob/master/llvmpy/gen/binding.py

The list of C++ types: https://github.com/llvmpy/llvmpy/blob/master/llvmpy/gen/binding.py#L218

