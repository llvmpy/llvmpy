OUTPUT = llrt
SOURCES = udivmod64.c

CLANG = clang
CF = -Wall -ansi
CF_TEST = $(CF) -ftrapv
CF_BUILD = $(CF) -O0 -emit-llvm
OUTDIR = ..

all: ir

ir: $(SOURCES)
	$(CLANG) -m32 $(CF_BUILD) -S -o $(OUTDIR)/$(OUTPUT)_x86.ll -c $(SOURCES)
	python ../tools/striptriple.py $(OUTDIR)/$(OUTPUT)_x86.ll
	$(CLANG) -m64 $(CF_BUILD) -S -o $(OUTDIR)/$(OUTPUT)_x86_64.ll -c $(SOURCES)
	python ../tools/striptriple.py $(OUTDIR)/$(OUTPUT)_x86_64.ll

lib$(OUTPUT).a: $(SOURCES)
	$(CLANG) $(CF) -o $@ -c $+

build-test:  lib$(OUTPUT).a
	for src in $(SOURCES); do \
		$(CLANG) $(CF_TEST) -o test_$${src%.*} test_$$src -L. -lllrt; \
	done;

test: build-test
	for src in $(SOURCES); do \
		echo "testing $${src%.*}";				 \
		python test_$${src%.*}.py > test_$${src%.*}.out;	 \
	done;

clean-test:
	rm -f *.out
	rm -f *.a
	for src in $(SOURCES); do \
		rm -f test_$${src%.*}	;\
	done;

clean-dist:
	rm $(OUTDIR)/*.ll

clean: clean-test clean-dist

udivmod64.c: udivmod64.h
