from binding import *
from namespace import llvm
from StringRef import StringRef
Target = llvm.Class()

@Target
class Target:
    _include_ = 'llvm/Support/TargetRegistry.h'

    getNext = Method(const(ptr(Target)))

    getName = Method(cast(StringRef, str))
    getShortDescription = Method(cast(StringRef, str))

    def _has():
        return Method(cast(Bool, bool))

    hasJIT = _has()
    hasTargetMachine = _has()
    hasMCAsmBackend = _has()
    hasMCAsmParser = _has()
    hasAsmPrinter = _has()
    hasMCDisassembler = _has()
    hasMCInstPrinter = _has()
    hasMCCodeEmitter = _has()
    hasMCObjectStreamer = _has()
    hasAsmStreamer = _has()
