from binding import *
from .namespace import llvm

DIBuilder = llvm.Class()

from .Module import Module
from .Value import Value, MDNode, Function, BasicBlock
from .Instruction import Instruction
from .DebugInfo import DIFile, DIEnumerator, DIType, DIBasicType, DIDerivedType, DICompositeType
from .DebugInfo import DIDescriptor, DIArray, DISubrange, DIGlobalVariable
from .DebugInfo import DIVariable, DISubprogram, DINameSpace, DILexicalBlockFile
from .DebugInfo import DILexicalBlock
from .ADT.SmallVector import SmallVector_Value
from .ADT.StringRef import StringRef

unsigned_arg = cast(int, Unsigned)
stringref_arg = cast(str, StringRef)
bool_arg = cast(bool, Bool)
uint64_arg = cast(int, Uint64)
int64_arg = cast(int, Int64)

@DIBuilder
class DIBuilder:
    _include_ = 'llvm/DIBuilder.h'
    new = Constructor(ref(Module))
    delete = Destructor()

    if LLVM_VERSION <= (3, 3):
        getCU = Method(const(ptr(MDNode)))
    finalize = Method()

    createCompileUnit = Method(Void,
                               unsigned_arg,  # Lang
                               stringref_arg, # File
                               stringref_arg, # Dir
                               stringref_arg, # Producer
                               bool_arg,      # isOptimized
                               stringref_arg, # Flags,
                               unsigned_arg,  # RV
                               # stringref_arg, # SplitName LLVM3.3
                               )  #.require_only(7)

    createFile = Method(DIFile,
                        stringref_arg,  # Filename
                        stringref_arg,  # Directory
                        )

    createEnumerator = Method(DIEnumerator,
                              stringref_arg,    # Name
                              uint64_arg if LLVM_VERSION <= (3, 3) else int64_arg, # Val
                              )

    if LLVM_VERSION <= (3, 3):
        createNullPtrType = Method(DIType,
                                   stringref_arg,   # Name
                                   )
    else:
        createNullPtrType = Method(DIBasicType)


    createBasicType = Method(DIType,
                             stringref_arg,     # Name
                             uint64_arg,        # SizeIntBits,
                             uint64_arg,        # AlignInBits,
                             unsigned_arg,      # Encoding
                             )

    createQualifiedType = Method(DIType,
                                 unsigned_arg,  # Tag
                                 ref(DIType),   # FromTy
                                 )

    createPointerType = Method(DIType,
                               ref(DIType),  # PointeeTy
                               uint64_arg,   # SizeInBits
                               uint64_arg,   # AlignInBits
                               stringref_arg, # Name
                               ).require_only(2)

    createReferenceType = Method(DIType,
                                 unsigned_arg,  # Tag
                                 ref(DIType),   # RTy
                                 )

    createTypedef = Method(DIType,
                           ref(DIType),        # Ty
                           stringref_arg,     # Name
                           ref(DIFile),       # File
                           unsigned_arg,      # LineNo
                           ref(DIDescriptor), # Context
                           )

    createFriend = Method(DIType if LLVM_VERSION <= (3, 3) else DIDerivedType,
                          ref(DIType),   # Ty
                          ref(DIType), # FriendTy
                          )

    createInheritance = Method(DIType,
                               ref(DIType),       # Ty
                               ref(DIType),       # BaseTy
                               uint64_arg,        # BaseOffset
                               unsigned_arg,      # Flags
                               )

    createMemberType = Method(DIType,
                              ref(DIDescriptor),   # Scope
                              stringref_arg,        # Name
                              ref(DIFile),          # File
                              unsigned_arg,         # LineNo
                              uint64_arg,           # SizeInBits
                              uint64_arg,           # AlignInBits
                              uint64_arg,           # OffsetInBits
                              unsigned_arg,         # Flags
                              ref(DIType),          # Ty
                              )

    createClassType = Method(DIType,
                             ref(DIDescriptor),     # Scope
                             stringref_arg,         # Name
                             ref(DIFile),           # File
                             unsigned_arg,          # LineNum
                             uint64_arg,            # SizeInBits
                             uint64_arg,            # AlignInBits
                             uint64_arg,            # OffsetInBits,
                             unsigned_arg,          # Flags
                             ref(DIType),           # DerivedFrom
                             ref(DIArray),          # Elements
                             ptr(MDNode),           # VTableHolder = 0
                             ptr(MDNode),           # TemplateParms = 0
                             ).require_only(10)

    if LLVM_VERSION >= (3, 3):
        createStructType = Method(DIType,
                                  ref(DIDescriptor),   # Scope
                                  stringref_arg,        # Name
                                  ref(DIFile),          # File
                                  unsigned_arg,         # LineNumber
                                  uint64_arg,           # SizeInBits
                                  uint64_arg,           # AlignInBits
                                  unsigned_arg,         # Flags
                                  ref(DIType),          # DerivedFrom
                                  ref(DIArray),         # Elements
                                  unsigned_arg,         # RunTimeLang = 0
                                  ).require_only(9)
    else:
        createStructType = Method(DIType,
                                  ref(DIDescriptor),   # Scope
                                  stringref_arg,        # Name
                                  ref(DIFile),          # File
                                  unsigned_arg,         # LineNumber
                                  uint64_arg,           # SizeInBits
                                  uint64_arg,           # AlignInBits
                                  unsigned_arg,         # Flags
                                  ref(DIArray),         # Elements
                                  unsigned_arg,         # RunTimeLang = 0
                                  ).require_only(8)

    createUnionType = Method(DIType,
                             ref(DIDescriptor),     # Scope
                             stringref_arg,         # Name
                             ref(DIFile),           # File
                             unsigned_arg,          # LineNum
                             uint64_arg,            # SizeInBits
                             uint64_arg,            # AlignInBits
                             unsigned_arg,          # Flags
                             ref(DIArray),          # Elements
                             unsigned_arg,          # RunTimeLang = 0
                             ).require_only(8)

    createArrayType = Method(DIType,
                             uint64_arg,  # Size
                             uint64_arg,  # AlignInBits
                             ref(DIType),  # Ty
                             ref(DIArray),  # Subscripts
                             )

    createVectorType = Method(DIType if LLVM_VERSION <= (3, 3) else DICompositeType,
                             uint64_arg,  # Size
                             uint64_arg,  # AlignInBits
                             ref(DIType),  # Ty
                             ref(DIArray),  # Subscripts
                             )

    createEnumerationType = Method(DIType,
                                   ref(DIDescriptor),   # Scope
                                   stringref_arg,       # Name
                                   ref(DIFile),         # File
                                   unsigned_arg,        # LineNumber
                                   uint64_arg,          # SizeInBits
                                   uint64_arg,          # AlignInBits
                                   ref(DIArray),        # Elements
                                   ref(DIType),         # ClassType
                                   )

    createSubroutineType = Method(DIType,
                                  ref(DIFile),      # File
                                  ref(DIArray),     # ParameterTypes
                                  )

    createArtificialType = Method(DIType,
                                ref(DIType),      # Ty
                                )

    createObjectPointerType = Method(DIType,
                                ref(DIType),      # Ty
                                )

    #createTemporaryType = Method(DIType, ref(DIFile)).require_only(0)

    createForwardDecl = Method(DIType,
                               unsigned_arg,         # Tag
                               stringref_arg,        # Name
                               ref(DIDescriptor),    # scope
                               ref(DIFile),          # F
                               unsigned_arg,         # Line
                               unsigned_arg,         # RuntimeLang=0
                               uint64_arg,           # SizeInBits=0
                               uint64_arg,           # AlignInBits=0
                               ).require_only(5)

    retainType = Method(Void, ref(DIType))

    createUnspecifiedParameter = Method(DIDescriptor)

    getOrCreateArray = Method(DIArray,
                              ref(SmallVector_Value),   # Elements
                              )

    getOrCreateSubrange = Method(DISubrange,
                                 int64_arg,     # Lo
                                 int64_arg,     # Hi
                                 )

    createGlobalVariable = Method(DIGlobalVariable,
                                  stringref_arg,    # Name
                                  ref(DIFile),      # File
                                  unsigned_arg,     # LineNo
                                  ref(DIType),      # Ty
                                  bool_arg,         # isLocalToUnit
                                  ptr(Value),       # Val
                                  )

    createStaticVariable = Method(DIGlobalVariable,
                                  ref(DIDescriptor), # Context
                                  stringref_arg,     # Name
                                  stringref_arg,     # LinkageName
                                  ref(DIFile),       # File
                                  unsigned_arg,      # LineNo
                                  ref(DIType),       # Ty
                                  bool_arg,          # isLocalToUnit
                                  ptr(Value),        # Val
                                  )

    createLocalVariable = Method(DIVariable,
                                 unsigned_arg,      # Tag,
                                 ref(DIDescriptor), # Scope,
                                 stringref_arg,     # Name,
                                 ref(DIFile),       # File,
                                 unsigned_arg,      # LineNo,
                                 ref(DIType),       # Ty,
                                 bool_arg,          # AlwaysPreserve=false,
                                 unsigned_arg,      # Flags=0,
                                 unsigned_arg,      # ArgNo=0
                                 ).require_only(6)

    createComplexVariable = Method(DIVariable,
                                   unsigned_arg,        # Tag,
                                   ref(DIDescriptor),   # Scope,
                                   stringref_arg,       # Name,
                                   ref(DIFile),         # F,
                                   unsigned_arg,        # LineNo,
                                   ref(DIType),         # Ty,
                                   ref(SmallVector_Value),   # Addr,
                                   unsigned_arg,        # ArgNo=0,
                                   ).require_only(7)

    createFunction = Method(DISubprogram,
                            ref(DIDescriptor),  # Scope
                            stringref_arg,      # Name
                            stringref_arg,      # LinkageName
                            ref(DIFile),        # File
                            unsigned_arg,       # LineNo
                            ref(DIType if LLVM_VERSION <= (3, 3) else DICompositeType), # Ty
                            bool_arg,           # isLocalToUnit
                            bool_arg,           # isDefinition
                            unsigned_arg,       # ScopeLine
                            unsigned_arg,       # Flags=0
                            bool_arg,           # isOptimized=false
                            ptr(Function),      # *Fn=0
                            ptr(MDNode),        # *TParam=0,
                            ptr(MDNode),        # *Decl=0
                            ).require_only(9)


    createMethod = Method(DISubprogram,
                          ref(DIDescriptor),        # Scope
                          stringref_arg,            # Name
                          stringref_arg,            # LinkageName
                          ref(DIFile),              # File
                          unsigned_arg,             # LineNo
                          ref(DIType if LLVM_VERSION <= (3, 3) else DICompositeType), # Ty
                          bool_arg,                 # isLocalToUnit
                          bool_arg,                 # isDefinition
                          unsigned_arg,             # Virtuality=0
                          unsigned_arg,             # VTableIndex=0
                          ptr(MDNode),              # *VTableHolder=0
                          unsigned_arg,             # Flags=0
                          bool_arg,                 # isOptimized=false
                          ptr(Function),            # *Fn=0
                          ptr(MDNode),              # *TParam=0
                          ).require_only(8)


    createNameSpace = Method(DINameSpace,
                             ref(DIDescriptor),     # Scope,
                             stringref_arg,         # Name,
                             ref(DIFile),           # File,
                             unsigned_arg,          # LineNo
                             )

    createLexicalBlockFile = Method(DILexicalBlockFile,
                                    ref(DIDescriptor),  # Scope,
                                    ref(DIFile),        # File
                                    )

    createLexicalBlock = Method(DILexicalBlock,
                                ref(DIDescriptor),  # Scope,
                                ref(DIFile),        # File,
                                unsigned_arg,       # Line,
                                unsigned_arg,       # Col
                                )

    _insertDeclare_1 = Method(ptr(Instruction),
                           ptr(Value),          # Storage,
                           ref(DIVariable),     # VarInfo
                           ptr(BasicBlock),     # *InsertAtEnd
                           )
    _insertDeclare_1.realname = 'insertDeclare'

    _insertDeclare_2 = Method(ptr(Instruction),
                           ptr(Value),          # Storage,
                           ref(DIVariable),     # VarInfo
                           ptr(Instruction),     # *InsertBefore
                           )
    _insertDeclare_2.realname = 'insertDeclare'

    @CustomPythonMethod
    def insertDeclare(self, storage, varinfo, insertpt):
        if isinstance(insertbefore, _api.llvm.Instruction):
            return self._insertDeclare_2(storage, varinfo, insertpt)
        else:
            return self._insertDeclare_1(storage, varinfo, insertpt)

    _insertDbgValueIntrinsic_1 = Method(ptr(Instruction),
                                        ptr(Value),        # *Val
                                        uint64_arg,        # Offset
                                        ref(DIVariable),   # VarInfo
                                        ptr(BasicBlock),   # *InsertAtEnd
                                        )
    _insertDbgValueIntrinsic_1.realname = 'insertDbgValueIntrinsic'

    _insertDbgValueIntrinsic_2 = Method(ptr(Instruction),
                                        ptr(Value),        # *Val
                                        uint64_arg,        # Offset
                                        ref(DIVariable),   # VarInfo
                                        ptr(Instruction),   # *InsertAtEnd
                                        )
    _insertDbgValueIntrinsic_2.realname = 'insertDbgValueIntrinsic'


    @CustomPythonMethod
    def insertDbgValueIntrinsic(self, storage, varinfo, insertpt):
        if isinstance(insertbefore, _api.llvm.Instruction):
            return self._insertDbgValueIntrinsic_2(storage, varinfo, insertpt)
        else:
            return self._insertDbgValueIntrinsic_1(storage, varinfo, insertpt)
