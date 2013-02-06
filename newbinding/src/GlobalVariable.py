from binding import *
from namespace import llvm

from GlobalValue import GlobalValue
GlobalVariable = llvm.Class(GlobalValue)

from Constant import Constant
from Module import Module
from Type import Type
from ADT.StringRef import StringRef

@GlobalVariable
class GlobalVariable:
    ThreadLocalMode = Enum('''NotThreadLocal, GeneralDynamicTLSModel, 
                              LocalDynamicTLSModel, InitialExecTLSModel,
                              LocalExecTLSModel
                           ''')

    new = Constructor(ref(Module),
                      ptr(Type),
                      cast(bool, Bool), # is constant
                      GlobalValue.LinkageTypes,
                      ptr(Constant), # initializer -- can be None
                      cast(str, StringRef), # name
                      ptr(GlobalVariable), # insert before
                      ThreadLocalMode,
                      cast(int, Unsigned), # address-space
                 #     cast(bool, Bool), # externally initialized
                      ).require_only(5)

    setThreadLocal = Method(Void, cast(bool, Bool))
    setThreadLocalMode = Method(Void, ThreadLocalMode)
    isThreadLocal = Method(cast(Bool, bool))

    isConstant = Method(cast(Bool, bool))
    setConstant = Method(Void, ptr(Constant))

    setInitializer = Method(Void, ptr(Constant))
    getInitializer = Method(ptr(Constant))
    hasInitializer = Method(cast(Bool, bool))

    hasUniqueInitializer = Method(cast(Bool, bool))
    hasDefinitiveInitializer = Method(cast(Bool, bool))

#    isExternallyInitialized = Method(cast(Bool, bool))
#    setExternallyinitialized = Method(Void, cast(bool, Bool))

    