from binding import *
from ..namespace import llvm

llvm.includes.add('llvm/Support/TargetSelect.h')

InitializeNativeTarget = llvm.Function('InitializeNativeTarget')
#llvm.Function('InitializeAllTargets')

InitializeNativeTargetAsmPrinter = llvm.Function(
                    'InitializeNativeTargetAsmPrinter', cast(Bool, bool))

InitializeNativeTargetAsmParser = llvm.Function(
                    'InitializeNativeTargetAsmParser', cast(Bool, bool))

InitializeNativeTargetDisassembler = llvm.Function(
                    'InitializeNativeTargetDisassembler', cast(Bool, bool))

