from binding import *
from src.namespace import llvm

llvm.includes.add('llvm/Support/TargetRegistry.h')

Target = llvm.Class()
TargetRegistry = llvm.Class()

from src.ADT.Triple import Triple
from src.ADT.StringRef import StringRef
from src.Target.TargetMachine import TargetMachine
from src.Target.TargetOptions import TargetOptions
from src.Support.CodeGen import Reloc, CodeModel, CodeGenOpt

@Target
class Target:
    getNext = Method(const(ptr(Target)))

    getName = Method(cast(StdString, str))
    getShortDescription = Method(cast(StdString, str))

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

    createTargetMachine = Method(ptr(TargetMachine),
                                 cast(str, StringRef), # triple
                                 cast(str, StringRef), # cpu
                                 cast(str, StringRef), # features
                                 ref(TargetOptions),
                                 Reloc.Model,       # = Reloc::Default
                                 CodeModel.Model,   # = CodeModel.Default
                                 CodeGenOpt.Level,  # = CodeGenOpt.Default
                                 ).require_only(4)


@TargetRegistry
class TargetRegistry:
    printRegisteredTargetsForVersion = StaticMethod()

    lookupTarget = CustomStaticMethod('TargetRegistry_lookupTarget',
                                        PyObjectPtr,         # const Target*
                                        cast(str, ConstCharPtr), # triple
                                        PyObjectPtr,         # std::string &Error
                                        )

    lookupTarget |= CustomStaticMethod('TargetRegistry_lookupTarget',
                                        PyObjectPtr,             # const Target*
                                        cast(str, ConstCharPtr), # arch
                                        ref(Triple),             # triple
                                        PyObjectPtr,         # std::string &Error
                                        )

    getClosestTargetForJIT = CustomStaticMethod(
                                    'TargetRegistry_getClosestTargetForJIT',
                                    PyObjectPtr,          # const Target*
                                    PyObjectPtr,          # std::string &Error
                                    )
