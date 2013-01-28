from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from BasicBlock import BasicBlock
from Instruction import ReturnInst, CallInst
from SmallVector import SmallVector_Value
from StringRef import StringRef
from Value import Value

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
    CreateRet = Method(ptr(ReturnInst), ptr(Value))

    _CreateCall = Method(ptr(CallInst), ptr(Value), ref(SmallVector_Value),
                        cast(str, StringRef))
    _CreateCall |= Method(ptr(CallInst), ptr(Value), ref(SmallVector_Value))
    _CreateCall.realname = 'CreateCall'

    @CustomPythonMethod
    def CreateCall(self, *args):
        import extra
        args = list(args)
        valuelist = args[1]
        args[1] = extra.make_small_vector_from_values(*valuelist)
        return IRBuilder._CreateCall(self, *args)
