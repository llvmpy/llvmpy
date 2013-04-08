================================
llvmpy: Python bindings for LLVM
================================

Home page
---------

http://www.llvmpy.org

Versions
--------

This package has been tested with LLVM 3.2, Python 2.6, 2.7 and 3.3.
Other Python versions may work.

Quickstart
----------

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
   
Common Build Problems
---------------------

1. If llvmpy cannot be imported due to "undefined symbol:
   _ZTIN4llvm24PassRegistrationListenerE", it is because RTTI is not enabled
   when building LLVM.  "_ZTIN4llvm24PassRegistrationListenerE" is the typeinfo
   of PassRegistrationListener class.

LICENSE
-------

llvmpy is distributed under the new BSD license, which is similar to the LLVM
license itself.
See the file called LICENSE for the full license text.
