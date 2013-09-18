import llvm

if llvm.version >= (3, 4):

    from llvm.target import TargetMachine
    from llvm import mc
    from llvm.mc import Disassembler

    llvm.target.initialize_all()

    def print_instructions(dasm, bs, align=None):
        branch_properties = [
            'is_branch',
            'is_cond_branch',
            'is_uncond_branch',
            'is_indirect_branch',
            'is_call',
            'is_return',
            'is_terminator',
            'is_barrier'
        ]

        print("print instructions")
        for (addr, data, inst) in dasm.decode(bs, 0x4000, align):

            if inst is None:
                print("\t0x%x => (bad)" % (addr))
            else:
                ops = ", ".join(map(lambda op: repr(op), inst.operands()))
                if isinstance(inst, mc.BadInstr):
                    print("\t0x%x (bad) ops = %s" % (addr, ops))
                else:
                    print("\t0x%x ops = %s" % (addr, ops))

                print("\t\topcode = 0x%x, flags = 0x%x, tsflags = 0x%x" % (inst.opcode, inst.flags, inst.ts_flags))
                for line in str(inst).split("\n"):
                    print("\t\t%-24s %s" % ("".join(map(lambda b: "%02x" % b, data))+":", line.strip()))

                for bp in branch_properties:
                    print("\t\t%-22s%r" % (bp+":", getattr(inst, bp)() ))


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
        "\xe5\x0b\x00\x20",
        "\x03\x30\x22\xe0", #bad instruction to test alignment
        "\x73\x20\xef\xe6", #bad instruction to test alignment
        "\x18\x00\x1b\xe5",
        "\x10\x30\xa0\xe3"
    ]
    print_instructions(Disassembler(arm), "".join(map(lambda s: s[::-1], code)), 4)
