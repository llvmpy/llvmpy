from binding import *
from .namespace import llvm
from .LLVMContext import LLVMContext

llvm.includes.add('llvm/Attributes.h')

Attributes = llvm.Class()
AttrBuilder = llvm.Class()


@Attributes
class Attributes:
    AttrVal = Enum('''None, AddressSafety, Alignment, AlwaysInline,
        ByVal, InlineHint, InReg, MinSize,
        Naked, Nest, NoAlias, NoCapture,
        NoImplicitFloat, NoInline, NonLazyBind, NoRedZone,
        NoReturn, NoUnwind, OptimizeForSize, ReadNone,
        ReadOnly, ReturnsTwice, SExt, StackAlignment,
        StackProtect, StackProtectReq, StructRet, UWTable, ZExt''')

    delete = Destructor()

    get = StaticMethod(Attributes, ref(LLVMContext), ref(AttrBuilder))


@AttrBuilder
class AttrBuilder:

    new = Constructor()
    delete = Destructor()

    clear = Method()

    addAttribute = Method(ref(AttrBuilder), Attributes.AttrVal)
    removeAttribute = Method(ref(AttrBuilder), Attributes.AttrVal)

    addAlignmentAttr = Method(ref(AttrBuilder), cast(int, Unsigned))


