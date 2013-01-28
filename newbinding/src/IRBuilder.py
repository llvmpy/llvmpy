from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from BasicBlock import BasicBlock
from Instruction import ReturnInst

IRBuilder = llvm.Class()

@IRBuilder
class IRBuilder:
    _include_ = 'llvm/IRBuilder.h'
    _realname_ = 'IRBuilder<>'

    new = Constructor(ref(LLVMContext))
    delete = Destructor()

    SetInsertPoint = Method(Void, ptr(BasicBlock))

    isNamePreserving = Method(cast(Bool, bool))

    CreateRetVoid = Method(ptr(ReturnInst))
