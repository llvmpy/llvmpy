================================
llvmpy: Python bindings for LLVM
================================

Important Note: Use llvmlite instead
------------------------------------

This project is **no longer maintained** and users are recommended to switch 
to `llvmlite <https://github.com/numba/llvmlite>`_, which is developed by llvmpy 
maintainers and numba developers.  For temporary compatibility with llvmpy, 
llvmlite emulates the `some API of llvmpy <https://github.com/numba/llvmlite/tree/master/llvmlite/llvmpy>`_.
This compatibility layer is enough to allow numba to transition to llvmlite with 
minimal code changes.  Keep in mind that this compatibility layer is **temporary**.
New code should be written for the llvmlite API, which is not very different.

Home page
---------

http://www.llvmpy.org

Versions
--------

This package has been tested with LLVM 3.3, Python 2.6, 2.7, 3.3 and 3.4.
Other Python versions may work.

Quickstart
----------

1. Get and extract LLVM 3.3 source tarball from
   `llvm.org <http://llvm.org/releases/download.html#3.3>`_.  Then, ``cd`` into
   the extracted directory.

2. Run ``./configure --enable-optimized --prefix=LLVM_INSTALL_PATH``.

    **Note**: Without the ``--enable-optimized`` flag, debug build will be
    selected.  Unless you are developing LLVM or llvmpy, it is recommended
    that the flag is used to reduce build time and binary size.

    **Note**: Use prefix to select the installation path.  It is recommended
    to separate your custom build from the default system package.  Please
    replace ``LLVM_INSTALL_PATH`` with your own path.

3. Run ``REQUIRES_RTTI=1 make install`` to build and install.

    **Note**: With LLVM 3.3, the default build configuration has C++ RTTI
    disabled.  However, llvmpy requires RTTI.

    **Note**: Use ``make -j2 install`` to enable concurrent build.
    Replace ``2`` with the actual number of processor you have.

4. Get llvm-py and install it::

   $ git clone https://github.com/llvmpy/llvmpy.git
   $ cd llvmpy
   $ LLVM_CONFIG_PATH=LLVM_INSTALL_PATH/bin/llvm-config python setup.py install
   
   **Note**: Some OS has a default python that may install to system 
   locations thus requiring root permission.  In that case, use::
   
   $ LLVM_CONFIG_PATH=LLVM_INSTALL_PATH/bin/llvm-config python setup.py install --user

   Run the tests::

   $ python -c "import llvm; llvm.test()"

5. See documentation at 'http://www.llvmpy.org' and examples
   under 'test'.

Ubuntu 14.04 installation instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install llvmpy with pip on ubuntu 14.04, follow these steps:

1. Make sure both the system version of llvm and version 3.3 is installed::

   $ sudo apt-get install llvm llvm-3.3

2. Install the non-released package of llvmpy that has support for
   multiple versions of llvm (as described in #126)::

   $ pip install https://pypi.python.org/packages/source/l/llvmpy/llvmpy-0.12.7-9-g60b512d.tar.gz

Common Build Problems
---------------------

1. If llvmpy cannot be imported due to "undefined symbol:
   _ZTIN4llvm24PassRegistrationListenerE", it is because RTTI is not enabled
   when building LLVM.  "_ZTIN4llvm24PassRegistrationListenerE" is the typeinfo
   of PassRegistrationListener class.

2. *LLVM3.3 ssize_t mismatch on 64-bit Windows.*
   Get patch from http://lists.cs.uiuc.edu/pipermail/llvm-commits/Week-of-Mon-20130701/180049.html

3. OSX 10.9 Mavericks uses libc++ by default but Anaconda distributes LLVM
   binaries link with the old libstdc++.  The two binaries are **incompatible**
   but there are no compile/link time warnings.  The resulting binaries may
   generate segmentation fault at runtime (probably due to ABI mismatch).
   **The Fix:** Use the following c++ flags:
   ``-std=libstdc++ -mmacosx-version-min=10.6``.

4. OSX 10.10 user will need to change the Makefile of LLVM 3.3 due to a version match error. 
   At line 574 of llvm3.3 Makefile.rules, modify 
   ``DARWIN_VERSION := $(shell echo $(DARWIN_VERSION)| sed -E 's/(10.[0-9]).*/\1/')``
   to ``DARWIN_VERSION := $(shell echo $(DARWIN_VERSION)| sed -E 's/(10.[0-9]+).*/\1/')``
   (Note the extra "+" in the regex). See https://github.com/llvmpy/llvmpy/issues/130 for the original issue.

LICENSE
-------

llvmpy is distributed under the new BSD license, which is similar to the LLVM
license itself.
See the file called LICENSE for the full license text.
