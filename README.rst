================================
llvmpy: Python bindings for LLVM
================================

Home page
---------

http://www.llvmpy.org

Versions
--------

This package has been tested with LLVM 3.1 and 3.2, Python 2.7 and Python 3.2.
Other Python versions should work.

Quickstart
----------

1. Get 3.1 or 3.2 version of LLVM, build it.  Make sure ``--enable-pic`` is 
   passed to LLVM's ``configure``.  
   
   For LLVM 3.2, make sure that environment variable ``REQUIRES_RTTI=1`` is 
   defined when running ``make``.  Otherwise, you may see "undefined symbol:
   _ZTIN4llvm24PassRegistrationListenerE".  Please refer to 
   http://llvm.org/docs/Packaging.html#c-features for details.

2. Get llvm-py and install it::

   $ git clone git@github.com:llvmpy/llvmpy.git
   $ cd llvmpy
   $ python setup.py install

   Run the tests::

   $ python -c "import llvm; llvm.test()"

3. See documentation at 'http://www.llvmpy.org' and examples
   under 'test'.

LICENSE
-------

llvmpy is distributed under the new BSD license, which is similar to the LLVM
license itself.
See the file called LICENSE for the full license text.
