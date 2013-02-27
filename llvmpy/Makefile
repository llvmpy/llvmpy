PYTHON = python

all: _api.so _capsule.so

_api.so _capsule.so: api.cpp capsule.cpp
	$(PYTHON) setup.py build_ext --inplace

api.cpp api/__init__.py: src/*.py include/llvm_binding/*.h gen/gen.py gen/binding.py
	$(PYTHON) gen/gen.py api src
	
clean: cleantemp
	rm -f _api.so _capsule.so
	rm -rf api
	
cleantemp:
	rm -f api.cpp

check: _api.so api/__init__.py
	$(PYTHON) test_binding.py
	
@PHONY: all clean check
