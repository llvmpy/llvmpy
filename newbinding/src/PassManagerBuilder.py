from binding import *
from namespace import llvm
from PassManager import PassManagerBase, FunctionPassManager

@llvm.Class()
class PassManagerBuilder:
    _include_ = 'llvm/Transforms/IPO/PassManagerBuilder.h'
    
    new = Constructor()
    delete = Destructor()

    populateFunctionPassManager = Method(Void, ref(FunctionPassManager))
    populateModulePassManager = Method(Void, ref(PassManagerBase))
    populateLTOPassManager = Method(Void,
                                    ref(PassManagerBase),
                                    cast(bool, Bool),
                                    cast(bool, Bool),
                                    cast(bool, Bool)).require_only(3)

