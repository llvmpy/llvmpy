from binding import *
from ..namespace import llvm
from ..ADT.StringRef import StringRef
from ..Module import Module
from ..LLVMContext import LLVMContext

llvm.includes.add('llvm/Bitcode/ReaderWriter.h')

ParseBitCodeFile = llvm.CustomFunction('ParseBitCodeFile',
                                       'llvm_ParseBitCodeFile',
                                       PyObjectPtr,    # returns Module*
                                       cast(bytes, StringRef),
                                       ref(LLVMContext),
                                       PyObjectPtr,         # file-like object
                                       ).require_only(2)

WriteBitcodeToFile = llvm.CustomFunction('WriteBitcodeToFile',
                                         'llvm_WriteBitcodeToFile',
                                         PyObjectPtr,   # return None
                                         ptr(Module),
                                         PyObjectPtr,   # file-like object
                                         )

getBitcodeTargetTriple = llvm.CustomFunction('getBitcodeTargetTriple',
                                             'llvm_getBitcodeTargetTriple',
                                             PyObjectPtr, # return str
                                             cast(str, StringRef),
                                             ref(LLVMContext),
                                             PyObjectPtr, # file-like object
                                             ).require_only(2)
