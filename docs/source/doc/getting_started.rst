
Introduction
============

`LLVM <http://www.llvm.org/>`_ (Low-Level Virtual Machine) provides
enough infrastructure to use it as the backend for your compiled, or
JIT-compiled language. It provides extensive optimization support, and
static and dynamic (JIT) backends for many platforms. See the website at
http://www.llvm.org/ to discover more.

Python bindings for LLVM provides a gentler learning curve for working
with the LLVM APIs. It should also be easier to create working
prototypes and experimental languages using this medium.

Together with `clang <http://clang.llvm.org/>`_ or
`llvm-gcc <http://llvm.org/releases/2.7/docs/CommandGuide/html/llvmgcc.html>`_ 
it also a provides a means to quickly instrument C and C++ sources. For e.g., 
llvm-gcc can be used to generate the LLVM assembly for a given C source file, 
which can then be loaded and manipulated (adding profiling code to every function,
say) using a llvmpy based Python script.

License
-------

Both LLVM and llvmpy are distributed under (different) permissive open
source licenses. llvmpy uses the `new BSD
license <http://opensource.org/licenses/bsd-license.php>`_. More
information is available
`here <https://github.com/numba/llvmpy/blob/master/LICENSE>`_.

Platforms
---------

llvmpy has been built/tested/reported to work on various GNU/Linux
flavours, BSD, Mac OS X; on i386 and amd64 architectures. Windows is not
supported, for a variety of reasons.

Versions
--------

llvmpy 0.9 requires version 3.1 of LLVM. It may not work with
previous versions.

llvmpy has been built and tested with Python 2.7 and 3.2. It should work with
earlier versions.


Installation
============

The Git repo of llvmpy is at https://github.com/llvmpy/llvmpy.git.
You'll need to build and install it before it can be used. At least the
following will be required for this:

-  C and C++ compilers (gcc/g++)
-  Python itself
-  Python development files (headers and libraries)
-  LLVM, either installed or built

On debian-based systems, the first three can be installed with the
command ``sudo apt-get install gcc g++ python python-dev``. Ensure that
your distro's repository has the appropriate version of LLVM!

It does not matter which compiler LLVM itself was built with (``g++``,
``llvm-g++`` or any other); llvmpy can be built with any compiler. It
has been tried only with gcc/g++ though.


LLVM and ``--enable-pic``
-------------------------

The result of an LLVM build is a set of static libraries and object
files. The llvmpy contains an extension package that is built into a
shared object (\_core.so) which links to these static libraries and
object files. It is therefore required that the LLVM libraries and
object files be built with the ``-fPIC`` option (generate position
independent code). Be sure to use the ``--enable-pic`` option while
configuring LLVM (default is no PIC), like this:

.. code-block:: bash
  
   $ ~/llvm ./configure --enable-pic --enable-optimized

llvm-config
-----------

In order to build llvmpy, it's build script needs to know from where it
can invoke the llvm helper program, ``llvm-config``. If you've installed
LLVM, then this will be available in your ``PATH``, and nothing further
needs to be done. If you've built LLVM yourself, or for any reason
``llvm-config`` is not in your ``PATH``, you'll need to pass the full
path of ``llvm-config`` to the build script.

You'll need to be 'root' to install llvmpy. Remember that your ``PATH``
is different from that of 'root', so even if ``llvm-config`` is in your
``PATH``, it may not be available when you do ``sudo``.

Steps
-----

Get 3.1 version of LLVM, build it. Make sure '--enable-pic' is passed to
LLVM's 'configure'.

Get llvmpy and install it:


.. code-block:: bash

   $ git clone git@github.com:numba/llvmpy.git
   $ cd llvmpy $ python setup.py install
