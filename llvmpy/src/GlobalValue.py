from binding import *
from .namespace import llvm
from .Value import GlobalValue
from .Module import Module
from .ADT.StringRef import StringRef

@GlobalValue
class GlobalValue:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/GlobalValue.h'
    else:
        _include_ = 'llvm/GlobalValue.h'

    LinkageTypes = Enum('''
        ExternalLinkage, AvailableExternallyLinkage, LinkOnceAnyLinkage,
        LinkOnceODRLinkage, LinkOnceODRAutoHideLinkage, WeakAnyLinkage,
        WeakODRLinkage, AppendingLinkage, InternalLinkage, PrivateLinkage,
        LinkerPrivateLinkage, LinkerPrivateWeakLinkage, DLLImportLinkage,
        DLLExportLinkage, ExternalWeakLinkage, CommonLinkage
        ''')

    VisibilityTypes = Enum('''DefaultVisibility,
                              HiddenVisibility,
                              ProtectedVisibility''')

    setLinkage = Method(Void, LinkageTypes)
    getLinkage = Method(LinkageTypes)

    setVisibility = Method(Void, VisibilityTypes)
    getVisibility = Method(VisibilityTypes)

    setLinkage = Method(Void, LinkageTypes)
    getLinkage = Method(LinkageTypes)

    getAlignment = Method(cast(Unsigned, int))
    setAlignment = Method(Void, cast(int, Unsigned))

    hasSection = Method(cast(Bool, bool))
    getSection = Method(cast(ConstStdString, str))
    setSection = Method(Void, cast(str, StringRef))

    isDiscardableIfUnused = Method(cast(Bool, bool))
    mayBeOverridden = Method(cast(Bool, bool))
    isWeakForLinker = Method(cast(Bool, bool))
    copyAttributesFrom = Method(Void, ptr(GlobalValue))
    destroyConstant = Method()
    isDeclaration = Method(cast(Bool, bool))
    removeFromParent = Method()
    eraseFromParent = Method()
    eraseFromParent.disowning = True

    getParent = Method(ownedptr(Module))
