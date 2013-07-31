from binding import *
from .namespace import llvm
from .Value import Value
from .DerivedTypes import FunctionType
from .ADT.StringRef import StringRef

if LLVM_VERSION >= (3, 3):
    llvm.includes.add('llvm/IR/InlineAsm.h')
else:
    llvm.includes.add('llvm/InlineAsm.h')

InlineAsm = llvm.Class(Value)

@InlineAsm
class InlineAsm:
    AsmDialect = Enum('AD_ATT', 'AD_Intel')
    ConstraintPrefix = Enum('''isInput, isOutput, isClobber''')

    get = StaticMethod(ptr(InlineAsm),
                       ptr(FunctionType),
                       cast(str, StringRef),    # AsmString
                       cast(str, StringRef),    # Constrains
                       cast(bool, Bool),        # hasSideEffects
                       cast(bool, Bool),        # isAlignStack
                       AsmDialect,              # default = AD_ATT
                       ).require_only(4)

