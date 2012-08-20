=================================
llvm-py: Python bindings for LLVM
=================================

Home page
---------

http://www.llvmpy.org

Versions
--------

This package has only been tested with LLVM 3.1, and Python 2.7, (not Python 3.x).

Quickstart
----------

1. Get 3.1 version of LLVM, build it.  Make sure ``--enable-pic`` is passed to
   LLVM's ``configure``.

2. Get llvm-py and install it::

   $ git clone git@github.com:llvmpy/llvmpy.git
   $ cd llvmpy
   $ python setup.py install

   Run the tests::

   $ python -c "import llvm; llvm.test()"

3. See documentation at 'http://www.llvmpy.org/pages.html' and examples
   under 'test'.

LICENSE
-------

llvmpy is distributed under the new BSD license, which is similar to the LLVM
license itself.
See the file called LICENSE for the full license text.
