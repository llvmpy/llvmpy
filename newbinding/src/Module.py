from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from StringRef import StringRef
from Constant import Constant
from DerivedTypes import FunctionType
from raw_ostream import raw_ostream
from AssemblyAnnotationWriter import AssemblyAnnotationWriter

# class Module
Module = llvm.Class()
Module.include.add("llvm/Module.h")

# Enumerators
Endianness = Module.Enum('AnyEndianness', 'LittleEndian', 'BigEndian')
PointerSize = Module.Enum('AnyPointerSize', 'Pointer32', 'Pointer64')

# Constructors & Destructors
new = Module.new(StringRef.From(str), LLVMContext.Ref)
delete = Module.delete()

# Module Level Accessor
getModuleIdentifier = Module.method(ConstStdString.To(str))
getDataLayout = Module.method(ConstStdString.To(str))
getTargetTriple = Module.method(ConstStdString.To(str))
getEndianness = Module.method(Endianness)
getPointerSize = Module.method(PointerSize)
getContext = Module.method(LLVMContext.Ref)
getModuleInlineAsm = Module.method(ConstStdString.To(str))

# Module Level Mutators
setModuleIdentifier = Module.method(Void, StringRef.From(str))
setDataLayout = Module.method(Void, StringRef.From(str))
setTargetTriple = Module.method(Void, StringRef.From(str))
setModuleInlineAsm = Module.method(Void, StringRef.From(str))
appendModuleInlineAsm = Module.method(Void, StringRef.From(str))

# Function Accessors
getOrInsertFunction = Module.method(Constant.Pointer, StringRef.From(str), FunctionType.Pointer)

# Utilities
dump = Module.method(Void)
print_ = Module.method(Void, raw_ostream.Ref, AssemblyAnnotationWriter.Pointer)
print_.realname = 'print'
dropAllReferences = Module.method(Void)
