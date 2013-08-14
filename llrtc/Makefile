all:
	make -C lib

ir:
	make -C lib ir

test:
	make -C lib test

clean-test:
	make -C lib clean-test

clean-temp:
	make -C lib clean-temp

clean:
	make -C lib clean

install: ir
	make -C lib clean-test
	make -C lib clean-temp
	