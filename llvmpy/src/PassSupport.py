from binding import *
from .namespace import llvm

PassInfo = llvm.Class()

from src.Pass import Pass
from src.PassRegistry import PassRegistry

@PassInfo
class PassInfo:
    _include_ = 'llvm/PassSupport.h'

    createPass = Method(ptr(Pass))

llvm.Function('initializeCore', Void, ref(PassRegistry))
llvm.Function('initializeScalarOpts', Void, ref(PassRegistry))
llvm.Function('initializeVectorization', Void, ref(PassRegistry))
llvm.Function('initializeIPO', Void, ref(PassRegistry))
llvm.Function('initializeAnalysis', Void, ref(PassRegistry))
llvm.Function('initializeIPA', Void, ref(PassRegistry))
llvm.Function('initializeTransformUtils', Void, ref(PassRegistry))
llvm.Function('initializeInstCombine', Void, ref(PassRegistry))
llvm.Function('initializeInstrumentation', Void, ref(PassRegistry))
llvm.Function('initializeTarget', Void, ref(PassRegistry))
