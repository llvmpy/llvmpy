from binding import *
from ..namespace import llvm
from ..Module import Module
from ..LLVMContext import LLVMContext
from ..Support.SourceMgr import SMDiagnostic

llvm.includes.add('llvm/Assembly/Parser.h')

ParseAssemblyString = llvm.Function('ParseAssemblyString',
                                    ptr(Module),
                                    cast(str, ConstCharPtr),
                                    ptr(Module), # can be None
                                    ref(SMDiagnostic),
                                    ref(LLVMContext))
