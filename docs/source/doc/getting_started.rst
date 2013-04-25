
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
`here <https://github.com/llvmpy/llvmpy/blob/master/LICENSE>`_.

Platforms
---------

llvmpy has been built/tested/reported to work on various GNU/Linux
flavours, BSD, Mac OS X; on i386 and amd64 architectures. Windows is not
supported, for a variety of reasons.

Versions
--------

llvmpy 0.11.2 uses LLVM 3.2 (or at least 3.1). It may not work with
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

1. Get and extract LLVM 3.2 source tarball from
   `llvm.org <http://llvm.org/releases/download.html#3.2>`_.  Then, ``cd`` into
   the extracted directory.

2. Run ``./configure --enable-optimized --prefix=LLVM_INSTALL_PATH``.

    **Note**: Without the ``--enable-optimized`` flag, debug build will be
    selected.  Unless you are developing LLVM or llvmpy, it is recommended
    that the flag is used to reduce build time and binary size.
    
    **Note**: Use prefix to select the installation path.  It is recommended
    to separate your custom build from the default system package.  Please
    replace ``LLVM_INSTALL_PATH`` with your own path.

3. Run ``REQUIRES_RTTI=1 make`` to build.

    **Note**: With LLVM 3.2, the default build configuration has C++ RTTI 
    disabled.  However, llvmpy requires RTTI.

4. Get llvm-py and install it::

   $ git clone git@github.com:llvmpy/llvmpy.git
   $ cd llvmpy
   $ LLVM_CONFIG_PATH=LLVM_INSTALL_PATH/bin/llvm-config python setup.py install

   Run the tests::

   $ python -c "import llvm; llvm.test()"

5. See documentation at 'http://www.llvmpy.org' and examples
   under 'test'.
