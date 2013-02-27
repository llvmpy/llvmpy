from binding import *
from ..namespace import llvm
from .raw_ostream import raw_ostream

@llvm.Class(raw_ostream)
class formatted_raw_ostream:
    _include_ = 'llvm/Support/FormattedStream.h'
    _new = Constructor(ref(raw_ostream), cast(bool, Bool))

    @CustomPythonStaticMethod
    def new(stream, destroy=False):
        inst = formatted_raw_ostream._new(stream, destroy)
        inst.__underlying_stream = stream # to prevent it being freed first
        return inst

