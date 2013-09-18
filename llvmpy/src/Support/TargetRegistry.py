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

if LLVM_VERSION >= (3, 4):
    from src.MC import MCSubtargetInfo
    from src.MC import MCDisassembler
    from src.MC import MCRegisterInfo
    from src.MC import MCAsmInfo
    from src.MC import MCInstrInfo
    from src.MC import MCInstrAnalysis
    from src.MC import MCInstPrinter

@Target
class Target:
    getNext = Method(const(ownedptr(Target)))

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

    if LLVM_VERSION >= (3, 4):
        createMCSubtargetInfo = Method(ptr(MCSubtargetInfo),
                                       cast(str, StringRef), #triple
                                       cast(str, StringRef), #cpu
                                       cast(str, StringRef)  #features
                                       )

        createMCDisassembler = Method(ptr(MCDisassembler), ref(MCSubtargetInfo))

        createMCRegInfo = Method(ptr(MCRegisterInfo),
                                 cast(str, StringRef)        #Triple
                                 )

        createMCAsmInfo = Method(ptr(MCAsmInfo),
                                 const(ref(MCRegisterInfo)), #MRI
                                 cast(str, StringRef)        #Triple
                                 )

        createMCInstrInfo = Method(ptr(MCInstrInfo))

        createMCInstrAnalysis = Method(ptr(MCInstrAnalysis), const(ptr(MCInstrInfo)))

        createMCInstPrinter = Method(ptr(MCInstPrinter),
                                     cast(int, Unsigned),        #SyntaxVariant
                                     const(ref(MCAsmInfo)),      #MAI
                                     const(ref(MCInstrInfo)),    #MII
                                     const(ref(MCRegisterInfo)), #MRI
                                     const(ref(MCSubtargetInfo)) #STI
                                     )
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

    targetsList = CustomStaticMethod('TargetRegistry_targets_list', PyObjectPtr)

