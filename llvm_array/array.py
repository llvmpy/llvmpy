# This should be moved to llvmpy
# 
# There are different array kinds parameterized by eltype and nd
# 
# Contiguous or Fortran 
# struct {
#    eltype *data;
#    intp shape[nd]; 
# } contiguous_array(eltype, nd)
#
# struct {
#    eltype *data;
#    diminfo shape[nd];
# } strided_array(eltype, nd)
# 
# struct {
#    eltype *data;
#    intp shape[nd];
#    intp stride[nd];
# } strided_soa_array(eltype, nd)
#
# struct {
#   intp dim;
#   intp stride;
#} diminfo
#

import llvm.core as lc
from llvm.core import Type
import llvm_cbuilder.shortnames as C

CONTIGUOUS = 1 << 8
STRIDED = CONTIGUOUS + 1
STRIDED_SOA = CONTIGUOUS + 2

array_kinds = (CONTIGUOUS, STRIDED, STRIDED_SOA)

void_type = C.void
int_type = C.int
char_type = C.char
int16_type = C.int16
intp_type = C.intp

diminfo_type = Type.struct([intp_type,    # shape
                            intp_type     # stride
                            ], name='diminfo')

# This is the way we define LLVM arrays. 
def cont_array_type(nd, el_type=char_type, name=''):
    terms = [Type.pointer(el_type),        # data
             Type.array(intp_type, nd)     # shape
            ]
    return Type.struct(terms, name=name)

def strided_array_type(nd, el_type=char_type, name=''):
    terms = [Type.pointer(el_type),        # data
             Type.array(diminfo_type, nd)  # diminfo
            ]
    return Type.struct(terms, name=name)

def strided_soa_type(nd, el_type=char_type, name=''):
    terms = [Type.pointer(el_type),     # data
             Type.array(intp_type, nd), # shape[nd]
             Type.array(intp_type, nd)  # strides[nd]
            ]
    return Type.struct(terms, name=name)

def check_array(arrtyp):
    if not isinstance(arrtyp, lc.StructType):
        return None
    if arrtyp.element_count not in [2, 3]:
        return None
    if not isinstance(arrtyp.elements[0], lc.PointerType) or \
        not isinstance(arrtyp.elements[1], lc.ArrayType):
        return None

    data_type = arrtyp.elements[0].pointee
    s1 = arrtyp.elements[1]
    nd = s1.count

    if arrtyp.element_count == 3:
        if not isinstance(arrtyp.elements[2], lc.ArrayType):
            return None
        s2 = arrtyp.elements[2]
        if s1.element != intp_type or s2.element != intp_type:
            return None
        if s1.count != s2.count:
            return None
        return STRIDED_SOA, nd, data_type

    if s1.element == diminfo_type:
        return STRIDED, nd, data_type
    elif s1.element == intp_type:
        return CONTIGUOUS, nd, data_type
    else:
        return None

def is_cont_array(arrtyp):
    if not isinstance(arrtyp, lc.StructType):
        return False
    if arrtyp.element_count != 2 or \
          not isinstance(arrtyp.elements[0], lc.PointerType) or \
          not isinstance(arrtyp.elements[1], lc.ArrayType):
        return False
    if arrtyp.elements[1].element != intp_type:
        return False
    return True

def is_strided_array(arrtyp, kind=diminfo_type):
    if not isinstance(arrtyp, lc.StructType):
        return False
    if arrtyp.element_count != 2 or \
          not isinstance(arrtyp.elements[0], lc.PointerType) or \
          not isinstance(arrtyp.elements[1], lc.ArrayType):
        return False
    if arrtyp.elements[1].element != kind:
        return False
    return True

def is_strided_soa_array(arrtyp):
    if not isinstance(arrtyp, lc.StructType):
        return False
    if arrtyp.element_count != 3 or \
          not isinstance(arrtyp.elements[0], lc.PointerType) or \
          not isinstance(arrtyp.elements[1], lc.ArrayType) or \
          not isinstance(arrtyp.elements[2], lc.ArrayType):
        return False
    s1, s2 = arrtyp.elements[1:]        
    if s1.element != intp_type or s2.element != intp_type:
        return False
    if s1.count != s2.count:
        return False
    return True

def test():
    arr = cont_array_type(5)
    assert check_array(arr) == (CONTIGUOUS, 5, char_type)
    arr = strided_array_type(4)
    assert check_array(arr) == (STRIDED, 4, char_type)
    arr = strided_soa_type(3)
    assert check_array(arr) == (STRIDED_SOA, 3, char_type)

if __name__ == '__main__':
    test()