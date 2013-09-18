from binding import *
from .namespace import llvm

from .ADT.StringRef import StringRef
from .Value import MDNode

DIDescriptor = llvm.Class()
DIEnumerator = llvm.Class(DIDescriptor)
DIScope = llvm.Class(DIDescriptor)
DIType = llvm.Class(DIScope)
DIBasicType = llvm.Class(DIType)
DIDerivedType = llvm.Class(DIType)
DICompositeType = llvm.Class(DIDerivedType)
DIFile = llvm.Class(DIScope)
DIArray = llvm.Class(DIDescriptor)
DISubrange = llvm.Class(DIDescriptor)
DIGlobalVariable = llvm.Class(DIDescriptor)
DIVariable = llvm.Class(DIDescriptor)
DISubprogram = llvm.Class(DIScope)
DINameSpace = llvm.Class(DIScope)
DILexicalBlockFile = llvm.Class(DIScope)
DILexicalBlock = llvm.Class(DIScope)

llvm.includes.add('llvm/DebugInfo.h')

return_bool = cast(Bool, bool)
return_stringref = cast(StringRef, str)
return_unsigned = cast(Unsigned, int)

@DIDescriptor
class DIDescriptor:
    new = Constructor(ptr(MDNode))
    delete = Destructor()

@DIScope
class DIScope:
    pass

@DIFile
class DIFile:
    # getFileNode = Method(ptr(MDNode)) # not in LLVM 3.2?
    Verify = Method(return_bool)

@DIEnumerator
class DIEnumerator:
    getName = Method(return_stringref)
    getEnumValue = Method(cast(Uint64 if LLVM_VERSION <= (3, 3) else Int64, int))
    Verify = Method(return_bool)

@DIType
class DIType:
    getName = Method(return_stringref)
    getLineNumber = Method(return_unsigned)
    Verify = Method(return_bool)

@DIBasicType
class DIBasicType:
    pass

@DIDerivedType
class DIDerivedType:
    pass

@DICompositeType
class DICompositeType:
    pass

@DIArray
class DIArray:
    Verify = Method(return_bool)

@DISubrange
class DISubrange:
    Verify = Method(return_bool)

@DIGlobalVariable
class DIGlobalVariable:
    Verify = Method(return_bool)

@DIVariable
class DIVariable:
    Verify = Method(return_bool)

@DISubprogram
class DISubprogram:
    Verify = Method(return_bool)

@DINameSpace
class DINameSpace:
    Verify = Method(return_bool)

@DILexicalBlockFile
class DILexicalBlockFile:
    Verify = Method(return_bool)

@DILexicalBlock
class DILexicalBlock:
    Verify = Method(return_bool)

