from binding import *
from namespace import llvm
from Value import GlobalValue

@GlobalValue
class GlobalValue:
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

