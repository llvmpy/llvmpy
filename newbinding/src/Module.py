from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from ADT.StringRef import StringRef
from Constant import Constant
from Function import Function
from DerivedTypes import FunctionType
from Support.raw_ostream import raw_ostream
from Assembly.AssemblyAnnotationWriter import AssemblyAnnotationWriter

@llvm.Class()
class Module:
    _include_ = "llvm/Module.h"
    # Enumerators
    Endianness = Enum('AnyEndianness', 'LittleEndian', 'BigEndian')
    PointerSize = Enum('AnyPointerSize', 'Pointer32', 'Pointer64')

    # Constructors & Destructors
    new = Constructor(cast(str, StringRef), ref(LLVMContext))
    delete = Destructor()

    # Module Level Accessor
    getModuleIdentifier = Method(cast(ConstStdString, str))
    getDataLayout = Method(cast(ConstStdString, str))
    getTargetTriple = Method(cast(ConstStdString, str))
    getEndianness = Method(Endianness)
    getPointerSize = Method(PointerSize)
    getContext = Method(ref(LLVMContext))
    getModuleInlineAsm = Method(cast(ConstStdString, str))

    # Module Level Mutators
    setModuleIdentifier = Method(Void, cast(str, StringRef))
    setDataLayout = Method(Void, cast(str, StringRef))
    setTargetTriple = Method(Void, cast(str, StringRef))
    setModuleInlineAsm = Method(Void, cast(str, StringRef))
    appendModuleInlineAsm = Method(Void, cast(str, StringRef))

    # Function Accessors
    getOrInsertFunction = Method(ptr(Constant), cast(str, StringRef),
                                 ptr(FunctionType))

    # Utilities
    dump = Method(Void)
    print_ = Method(Void, ref(raw_ostream), ptr(AssemblyAnnotationWriter))
    print_.realname = 'print'

    @CustomPythonMethod
    def __str__(self):
        import extra
        os = extra.make_raw_ostream_for_printing()
        self.print_(os, None)
        return os.str()

    dropAllReferences = Method()
