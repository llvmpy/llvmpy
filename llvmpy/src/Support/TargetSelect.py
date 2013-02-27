from binding import *
from ..namespace import llvm, default

llvm.includes.add('llvm/Support/TargetSelect.h')

InitializeNativeTarget = llvm.Function('InitializeNativeTarget')
InitializeNativeTargetAsmPrinter = llvm.Function(
                    'InitializeNativeTargetAsmPrinter', cast(Bool, bool))
InitializeNativeTargetAsmParser = llvm.Function(
                    'InitializeNativeTargetAsmParser', cast(Bool, bool))
InitializeNativeTargetDisassembler = llvm.Function(
                    'InitializeNativeTargetDisassembler', cast(Bool, bool))


#InitializeAllTargets = llvm.Function('InitializeAllTargets')
#InitializeAllTargetInfos = llvm.Function('InitializeAllTargetInfos')
#InitializeAllTargetMCs = llvm.Function('InitializeAllTargetMCs')
#InitializeAllAsmPrinters = llvm.Function('InitializeAllAsmPrinters')

if PTX_SUPPORT == 'PTX':
    LLVMInitializePTXTarget = default.Function('LLVMInitializePTXTarget')
    LLVMInitializePTXTargetInfo = default.Function('LLVMInitializePTXTargetInfo')
    LLVMInitializePTXTargetMC = default.Function('LLVMInitializePTXTargetMC')
    LLVMInitializePTXAsmPrinter = default.Function('LLVMInitializePTXAsmPrinter')

if PTX_SUPPORT == 'NVPTX':
    LLVMInitializeNVPTXTarget = default.Function('LLVMInitializeNVPTXTarget')
    LLVMInitializeNVPTXTargetInfo = default.Function('LLVMInitializeNVPTXTargetInfo')
    LLVMInitializeNVPTXTargetMC = default.Function('LLVMInitializeNVPTXTargetMC')
    LLVMInitializeNVPTXAsmPrinter = default.Function('LLVMInitializeNVPTXAsmPrinter')
