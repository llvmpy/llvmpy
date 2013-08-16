import llvm

if llvm.version >= (3, 4):

    from llvm import mc
    from llvm.mc import Disassembler
    from llvmpy import api

    llvm.initialize_all_target_components()

    def op_str(op):
       s = []
       if op.isValid():
           s.append("valid")
       else:
           s.append("invalid")

       if op.isReg():
           s.append("+reg(%d)" % op.getReg())
   
       if op.isImm():
           s.append("+imm(%d)" % op.getImm())

       if op.isFPImm():
           s.append("+fp-imm(%f)" % op.getFPImm())

       if op.isExpr():
           s.append("+expr")

       if op.isInst():
           s.append("+inst")

       return " ".join(s)

    def print_instructions(dasm, bs):
        for (offset, inst) in dasm.decode(bs):
            if inst is None:
                print("\t%r=>(bad): 0, []" % (offset))
            else:
                if  isinstance(inst, mc.BadInstr):
                    print("\t%r=>(bad)%r: %r" % (offset, inst, len(inst)))
                else:
                    print("\t%r=>%r: %r" % (offset, inst, len(inst)))
    
                for op in inst.operands():
                    print("\t\t%s" % op_str(op))


    print("x86:")
    print_instructions(Disassembler.x86(), "\x01\xc3\xc3\xcc\x90")
    print("x86-64:")
    print_instructions(Disassembler.x86_64(), "\x55\x48\x89\xe8")
    print("arm:")
    code = [
        "\xe9\x2d\x48\x00",
        "\xea\x00\x00\x06",
        "\xe2\x4d\xd0\x20",
        "\xe2\x8d\xb0\x04",
        "\xe5\x0b\x00\x20"
    ]
    print_instructions(Disassembler.arm(), "".join(map(lambda s: s[::-1], code)))
