import llvm

if llvm.version >= (3, 4):

    from llvm.target import TargetMachine
    from llvm import mc
    from llvm.mc import Disassembler

    llvm.target.initialize_all()

    def print_instructions(dasm, bs):
        for (offset, inst) in dasm.decode(bs, 0):
            if inst is None:
                print("\t%r=>(bad): 0, []" % (offset))
            else:
                if isinstance(inst, mc.BadInstr):
                    print("\t%r=>(bad)%r: %r" % (offset, inst, len(inst)))
                else:
                    print("\t%r=>%r: %r" % (offset, inst, len(inst)))
    
                for op in inst.operands():
                    print("\t\t%s" % repr(op))


    x86 = TargetMachine.x86()
    print("x86: LE=%s" % x86.is_little_endian())
    print_instructions(Disassembler(x86), "\x01\xc3\xc3\xcc\x90")

    x86_64 = TargetMachine.x86_64()
    print("x86-64: LE=%s" % x86_64.is_little_endian())
    print_instructions(Disassembler(x86_64), "\x55\x48\x89\xe8")

    arm = TargetMachine.arm()
    print("arm: LE=%s" % arm.is_little_endian())
    code = [
        "\xe9\x2d\x48\x00",
        "\xea\x00\x00\x06",
        "\xe2\x4d\xd0\x20",
        "\xe2\x8d\xb0\x04",
        "\xe5\x0b\x00\x20"
    ]
    print_instructions(Disassembler(arm), "".join(map(lambda s: s[::-1], code)))
