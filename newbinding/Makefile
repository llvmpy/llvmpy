PYTHON = python

PYMODS = raw_ostream SmallVector Type DerivedTypes StringRef 
PYMODS += Value User Constant
PYMODS += LLVMContext AssemblyAnnotationWriter Module


all: _api.so _capsule.so

_api.so _capsule.so: api.cpp capsule.cpp
	$(PYTHON) setup.py build_ext --inplace

api.cpp api.py: src/*.py include/llvm_binding/*.h
	$(PYTHON) gen.py api src $(PYMODS)
	
clean: cleantemp
	rm -f _api.so _capsule.so
	
cleantemp:
	rm -f api.cpp api.py
	rm -f src/*.pyc


check: _api.so api.py
	$(PYTHON) test2.py
	
@PHONY: all clean check
