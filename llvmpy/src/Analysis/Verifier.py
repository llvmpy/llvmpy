from binding import *
from ..namespace import llvm
from ..Module import Module
from ..Value import Function

llvm.includes.add('llvm/Analysis/Verifier.h')

VerifierFailureAction = llvm.Enum('VerifierFailureAction',
                                  '''AbortProcessAction
                                     PrintMessageAction
                                     ReturnStatusAction''')

verifyModule = llvm.CustomFunction('verifyModule',
                                   'llvm_verifyModule',
                                   PyObjectPtr,  # boolean -- failed?
                                   ref(Module),
                                   VerifierFailureAction,
                                   PyObjectPtr,       # errmsg
                                   )

verifyFunction = llvm.Function('verifyFunction',
                               cast(Bool, bool),  # failed?
                               ref(Function),
                               VerifierFailureAction)

