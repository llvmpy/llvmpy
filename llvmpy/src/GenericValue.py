from binding import *
from .namespace import llvm
from .Type import Type

GenericValue = llvm.Class()

@GenericValue
class GenericValue:
    delete = Destructor()

    def _factory(name, *argtys):
         return CustomStaticMethod('GenericValue_' + name,
                                   ptr(GenericValue), *argtys)

    CreateFloat = _factory('CreateFloat', cast(float, Float))

    CreateDouble = _factory('CreateDouble', cast(float, Float))

    CreateInt = _factory('CreateInt', ptr(Type),
                         cast(int, UnsignedLongLong), cast(bool, Bool))

    CreatePointer = _factory('CreatePointer', cast(int, VoidPtr))

    def _accessor(name, *argtys):
        return CustomMethod('GenericValue_' + name, *argtys)

    valueIntWidth = _accessor('ValueIntWidth', cast(Unsigned, int))

    toSignedInt = _accessor('ToSignedInt', cast(LongLong, int))
    toUnsignedInt = _accessor('ToUnsignedInt', cast(UnsignedLongLong, int))

    toFloat = _accessor('ToFloat', cast(Double, float), ptr(Type))

    toPointer = _accessor('ToPointer', cast(VoidPtr, int))
