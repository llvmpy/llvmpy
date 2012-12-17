from llvm.core import Type

void = Type.void()
char = Type.int(8)
short = Type.int(16)
int = Type.int(32)
int16 = short
int32 = int
int64 = Type.int(64)

float = Type.float()
double = Type.double()

# platform dependent

def _determine_sizes():
    import ctypes
    # Makes following assumption:
    # sizeof(py_ssize_t) == sizeof(ssize_t) == sizeof(size_t)
    any_size_t = getattr(ctypes, 'c_ssize_t', ctypes.c_size_t)
    return ctypes.sizeof(ctypes.c_void_p) * 8, ctypes.sizeof(any_size_t) * 8

pointer_size, _py_ssize_t_bits = _determine_sizes()

intp = {32: int32, 64: int64}[pointer_size]

npy_intp = Type.int(pointer_size)
py_ssize_t = Type.int(_py_ssize_t_bits)

# pointers

pointer = Type.pointer

void_p = pointer(char)
char_p = pointer(char)
npy_intp_p = pointer(npy_intp)

# vector
def vector(ty, ct):
    return Type.vector(ty, 4)

