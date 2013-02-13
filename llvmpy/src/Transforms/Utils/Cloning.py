from binding import *
from src.namespace import llvm

llvm.includes.add('llvm/Transforms/Utils/Cloning.h')

InlineFunctionInfo = llvm.Class()


from src.Module import Module
from src.Instruction import CallInst

@InlineFunctionInfo
class InlineFunctionInfo:
    new = Constructor()
    delete = Destructor()


CloneModule = llvm.Function('CloneModule', ptr(Module), ptr(Module))

InlineFunction = llvm.Function('InlineFunction',
                               cast(Bool, bool),    # bool --- failed
                               ptr(CallInst),
                               ref(InlineFunctionInfo),
                               cast(bool, Bool),    # insert lifetime = true
                               ).require_only(2)
