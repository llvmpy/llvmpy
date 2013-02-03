from binding import *
from ..namespace import llvm

llvm.includes.add('llvm/Support/TargetSelect.h')

InitializeNativeTarget = llvm.Function('InitializeNativeTarget')
#llvm.Function('InitializeAllTargets')

