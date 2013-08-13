DIRECTORIES = divmod

all:
	for mydir in $(DIRECTORIES); do \
		make -C $$mydir; \
	done

test:
	for mydir in $(DIRECTORIES); do \
		make -C $$mydir test; \
	done

clean-test:
	for mydir in $(DIRECTORIES); do \
		make -C $$mydir clean-test; \
	done

clean:
	for mydir in $(DIRECTORIES); do \
		make -C $$mydir clean; \
	done