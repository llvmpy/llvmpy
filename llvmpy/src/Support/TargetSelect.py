import os
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

InitializeAllTargets = llvm.Function('InitializeAllTargets')
InitializeAllTargetInfos = llvm.Function('InitializeAllTargetInfos')
InitializeAllTargetMCs = llvm.Function('InitializeAllTargetMCs')
InitializeAllAsmPrinters = llvm.Function('InitializeAllAsmPrinters')
InitializeAllDisassemblers = llvm.Function('InitializeAllDisassemblers')
InitializeAllAsmParsers = llvm.Function('InitializeAllAsmParsers')


for target in TARGETS_BUILT:
    decls = 'Target', 'TargetInfo', 'TargetMC', 'AsmPrinter'
    for k in map(lambda x: 'LLVMInitialize%s%s' % (target, x), decls):
        if k == 'LLVMInitializeCppBackendAsmPrinter':
            continue
        globals()[k] = default.Function(k)

