PYMODS = _Debug raw_ostream Type DerivedTypes LLVMContext StringRef AssemblyAnnotationWriter Module

all: _api.so _capsule.so

_api.so _capsule.so: api.cpp capsule.cpp
	python setup.py build_ext --inplace

api.cpp api.py: src/*.py include/llvm_binding/*.h
	python gen.py api src $(PYMODS)
	
clean:
	rm -f _api.so _capsule.so
	rm -f api.cpp api.py

check: _api.so api.py
	python test2.py
	
@PHONY: all clean check
