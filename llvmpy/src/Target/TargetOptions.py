from binding import *
from src.namespace import llvm

llvm.includes.add('llvm/Target/TargetOptions.h')

TargetOptions = llvm.Class()

@TargetOptions
class TargetOptions:
    new = Constructor()
    delete = Destructor()

