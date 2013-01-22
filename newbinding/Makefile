PYMODS = _Debug raw_ostream Type DerivedTypes LLVMContext StringRef AssemblyAnnotationWriter Module

all: _api.so _capsule.so

_api.so _capsule.so: api.cpp capsule.cpp
	python setup.py build_ext --inplace


api.cpp api.py: binding/*.py include/llvm_binding/*.h
	cd binding; python gen.py api $(PYMODS)
	mv binding/api.cpp api.cpp
	mv binding/api.py api.py
	
clean:
	rm -f _api.so _capsule.so
	rm -f api.cpp api.py

	
