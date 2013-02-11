from binding import *
from ..namespace import llvm

llvm.includes.add('llvm/Support/SourceMgr.h')

@llvm.Class()
class SMDiagnostic:
    new = Constructor()
    delete = Destructor()

