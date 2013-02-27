from binding import *
from ..namespace import llvm
from ..Pass import Pass

llvm.includes.add('llvm/Transforms/IPO.h')

createFunctionInliningPass = llvm.Function('createFunctionInliningPass',
                                           ptr(Pass),
                                           cast(int, Unsigned)).require_only(0)
