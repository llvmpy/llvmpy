cat ~/local/include/llvm/Instruction.def | grep '^HANDLE' | sed -e 's/^[^(]*(//' | sed -e 's#).*$##' | sed -e 's/,[^,]*$//' | sed -e 's/,//' | awk '{printf("OPCODE_%-14s = %s\n", $2, $1);}'
