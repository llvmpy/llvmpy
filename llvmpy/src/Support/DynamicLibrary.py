from binding import *
from ..namespace import sys
from ..ADT.StringRef import StringRef

DynamicLibrary = sys.Class()


@DynamicLibrary
class DynamicLibrary:
    _include_ = 'llvm/Support/DynamicLibrary.h'
    isValid = Method(cast(Bool, bool))
    getAddressOfSymbol = Method(cast(VoidPtr, int), cast(str, ConstCharPtr))

    LoadPermanentLibrary = CustomStaticMethod(
                          'DynamicLibrary_LoadLibraryPermanently',
                          PyObjectPtr,             # bool --- failed?
                          cast(str, ConstCharPtr), # filename
                          PyObjectPtr,             # std::string * errmsg = 0
                          ).require_only(1)

    SearchForAddressOfSymbol = StaticMethod(cast(VoidPtr, int), # address
                                            cast(str, ConstCharPtr), # symName
                                            )

    AddSymbol = StaticMethod(Void,
                             cast(str, StringRef), # symbolName
                             cast(int, VoidPtr),   # address
                             )

    getPermanentLibrary = CustomStaticMethod(
                          'DynamicLibrary_getPermanentLibrary',
                          PyObjectPtr,
                          cast(str, ConstCharPtr), # filename
                          PyObjectPtr,             # std::string * errmsg = 0
                          ).require_only(1)
