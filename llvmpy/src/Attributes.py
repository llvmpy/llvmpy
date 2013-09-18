from binding import *
from .namespace import llvm
from .LLVMContext import LLVMContext

if LLVM_VERSION >= (3, 3):
    llvm.includes.add('llvm/IR/Attributes.h')
else:
    llvm.includes.add('llvm/Attributes.h')


AttrBuilder = llvm.Class()

if LLVM_VERSION >= (3, 3):
    Attribute = llvm.Class()
    AttributeSet = llvm.Class()
else:
    Attributes = llvm.Class()


if LLVM_VERSION >= (3, 3):
    @Attribute
    class Attribute:
        AttrKind = Enum('''None, Alignment, AlwaysInline,
                  ByVal, InlineHint, InReg,
                  MinSize, Naked, Nest, NoAlias,
                  NoBuiltin, NoCapture, NoDuplicate, NoImplicitFloat,
                  NoInline, NonLazyBind, NoRedZone, NoReturn,
                  NoUnwind, OptimizeForSize, ReadNone, ReadOnly,
                  Returned, ReturnsTwice, SExt, StackAlignment,
                  StackProtect, StackProtectReq, StackProtectStrong, StructRet,
                  SanitizeAddress, SanitizeThread, SanitizeMemory, UWTable,
                  ZExt, EndAttrKinds''')

        delete = Destructor()

        get = StaticMethod(Attribute,
                           ref(LLVMContext),
                           AttrKind,
                           cast(int, Uint64)).require_only(2)

    @AttrBuilder
    class AttrBuilder:

        new = Constructor()
        delete = Destructor()

        clear = Method()

        addAttribute = Method(ref(AttrBuilder), Attribute.AttrKind)
        removeAttribute = Method(ref(AttrBuilder), Attribute.AttrKind)

        addAlignmentAttr = Method(ref(AttrBuilder), cast(int, Unsigned))

    @AttributeSet
    class AttributeSet:
        delete = Destructor()

        get = StaticMethod(AttributeSet,
                           ref(LLVMContext),
                           cast(int, Unsigned),
                           ref(AttrBuilder))

else:
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


