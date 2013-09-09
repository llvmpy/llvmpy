OUTPUT = llrt
SOURCES = udivmod64.c sdivmod64.c div64.c mod64.c
TESTS = test_udivmod64.c test_sdivmod64.c

CLANG = clang
LLVM_LINK = llvm-link
CF = -Wall -ansi
CF_TEST = $(CF) -ftrapv
CF_BUILD = $(CF) -O0 -emit-llvm
OUTDIR = ..
STRIPPER = ../tools/striptriple.py

all: ir

ir: $(OUTDIR)/$(OUTPUT)_x86.ll $(OUTDIR)/$(OUTPUT)_x86_64.ll

$(OUTDIR)/$(OUTPUT)_x86.ll: $(SOURCES:.c=_x86.bc)
	$(LLVM_LINK) -S $+ -o $@
	python $(STRIPPER) $@

$(OUTDIR)/$(OUTPUT)_x86_64.ll: $(SOURCES:.c=_x86_64.bc)
	$(LLVM_LINK) -S $+ -o $@
	python $(STRIPPER) $@

build-test: $(SOURCES:.c=.o) $(TESTS:.c=.run)

lib$(OUTPUT).a: $(SOURCES:.c=.o)
	$(CLANG) -static $+ -o $@

test: $(TESTS:.c=.run)
	for src in $+; do \
		echo "testing $${src}";				 \
		python $${src%.*}.py > $${src%.*}.out;	 \
	done;

clean-test:
	rm -f *.out
	rm -f *.o
	rm -f *.run

clean-dist: clean-temp
	rm -f *.ll

clean-temp:
	rm -f *.bc
	rm -f *.o
	rm -f *.out

clean: clean-test clean-dist

%.c: llrt.h

%_x86.bc: %.c
	$(CLANG) -m32 $(CF_BUILD) -c $< -o $@

%_x86_64.bc: %.c
	$(CLANG) -m64 $(CF_BUILD) -c $< -o $@

%.o: %.c
	$(CLANG) $(CF_TEST) -c $<

%.run: %.c
	$(CLANG) $(CF_TEST) -o $@ $+

test_udivmod64.run: udivmod64.o
test_sdivmod64.run: udivmod64.o sdivmod64.o
