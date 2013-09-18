from llvmpy.api import llvm;
llvm.InitializeAllTargets()
llvm.InitializeAllTargetInfos()
llvm.InitializeAllTargetMCs()
llvm.InitializeAllAsmPrinters()
llvm.InitializeAllDisassemblers()
llvm.InitializeAllAsmParsers()

mthds = (
    ("description:",            "getShortDescription"),
    ("has JIT:",                "hasJIT"             ),
    ("has target machine:",     "hasTargetMachine"   ),
    ("has asm backend:",        "hasMCAsmBackend"    ),
    ("has asm parser:",         "hasMCAsmParser"     ),
    ("has asm printer:",        "hasAsmPrinter"      ),
    ("has disassembler:",       "hasMCDisassembler"  ),
    ("has inst printer:",       "hasMCInstPrinter"   ),
    ("has code emitter:",       "hasMCCodeEmitter"   ),
    ("has object streamer:",    "hasMCObjectStreamer"),
    ("has asm streamer:",       "hasAsmStreamer"     )
)

for target in llvm.TargetRegistry.targetsList():
    print("target %s" % target.getName())
    fmt = "%3s%-25s%r"
    for (desc, mthd) in mthds:
        print(fmt % ("", desc, getattr(target, mthd)()))

    print("")

