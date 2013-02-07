from binding import *
from src.namespace import llvm
from src.Module import Module

llvm.includes.add('llvm/Transforms/Utils/Cloning.h')
CloneModule = llvm.Function('CloneModule', ptr(Module), ptr(Module))


