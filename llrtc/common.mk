CLANG = clang
CF = -Wall -ansi
OUTDIR = ..

all: ir

$(OUTPUT).c:  $(OUTPUT).h

$(OUTPUT): test.c $(OUTPUT).c
	$(CLANG) $(CF) -ftrapv -o $@ $+

test: $(OUTPUT)
	python test.py

ir: 	
	CLANG -m32 $(CF) -O0 -emit-llvm -S $(OUTPUT).c -o $(OUTDIR)/x86/$(OUTPUT).ll
	CLANG -m64 $(CF) -O0 -emit-llvm -S $(OUTPUT).c -o $(OUTDIR)/x86_64/$(OUTPUT).ll
	python ../tools/striptriple.py $(OUTDIR)/x86/$(OUTPUT).ll
	python ../tools/striptriple.py $(OUTDIR)/x86_64/$(OUTPUT).ll

clean-test:
	rm -f $(OUTPUT)

clean: clean-test
	rm -f $(OUTDIR)/x86/$(OUTPUT).ll
	rm -f $(OUTDIR)/x86_64/$(OUTPUT).ll
