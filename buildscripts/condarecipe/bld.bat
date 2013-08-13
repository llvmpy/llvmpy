set LLVMPY_DYNLINK=0
set INCLUDE=%LIBRARY_INC%
set LIBPATH=%LIBRARY_LIB%
set LIB=%LIBRARY_LIB%
%PYTHON% setup.py install
if errorlevel 1 exit 1
