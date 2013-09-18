import llvm.target
from llvmpy import api, extra


def main():
    if llvm.version < (3, 4):
        return 0

    triple = "i386--"

    print("init start")
    api.llvm.InitializeAllTargets()
    api.llvm.InitializeAllTargetInfos()
    api.llvm.InitializeAllTargetMCs()
    api.llvm.InitializeAllAsmParsers()
    api.llvm.InitializeAllAsmPrinters()
    api.llvm.InitializeAllDisassemblers()
    print("init done\n")

    tm = llvm.target.TargetMachine.x86()
    if not tm:
        print("error: failed to lookup target x86 \n")
        return 1

    print("created target machine\n")

    MII = tm.instr_info
    if not MII:
        print("error: no instruction info for target " + triple + "\n")
        return 1

    print("created instr info\n")
    MID = MII.get(919) #int3
    print("INT3(%d): flags=0x%x, tsflags=0x%x\n" % (MID.getOpcode(), MID.getFlags(), MID.TSFlags))

    return 0

exit(main())
