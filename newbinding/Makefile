PYTHON = python

all: _api.so _capsule.so

_api.so _capsule.so: api.cpp capsule.cpp
	$(PYTHON) setup.py build_ext --inplace

api.cpp api.py: src/*.py include/llvm_binding/*.h gen/gen.py gen/binding.py
	$(PYTHON) gen/gen.py api src
	
clean: cleantemp
	rm -f _api.so _capsule.so
	
cleantemp:
	rm -f api.cpp api.py
	rm -f src/*.pyc src/Transforms/*.pyc src/ADT/*.pyc src/Assembly/*.pyc src/CodeGen/*.pyc src/ExecutionEngine/*.pyc src/Target/*.pyc src/Transforms/*.pyc


check: _api.so api.py
	$(PYTHON) test_binding.py
	
@PHONY: all clean check
