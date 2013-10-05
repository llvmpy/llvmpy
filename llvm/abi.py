'''
Provide C ABI information

Reference to 
- http://clang.llvm.org/doxygen/classclang_1_1ABIArgInfo.html
- http://clang.llvm.org/doxygen/CodeGen_2TargetInfo_8cpp_source.html
    See X86_32ABIInfo, computeInfo, classifyArgumentType
'''
from collections import namedtuple
import llvm.core as lc

AGGREGATE_TYPES = frozenset([lc.TYPE_STRUCT, lc.TYPE_ARRAY])

class ABIArgInfo(object):
    '''
    ABI argument info

    Try to be a close translation of clang::ABIArgInfo.
    (See http://clang.llvm.org/doxygen/classclang_1_1ABIArgInfo.html)
    But, this is for C not C++.
    '''
    __slots__ = ['_kind', '_typedata', '_paddingtype', '_uintdata',
                 '_booldata0', '_booldata1', '_inreg', '_paddinginreg']

    # Enum for argument info kind
    DIRECT = 0
    EXTEND = 1
    IGNORE = 2
    INDIRECT = 3
    EXPAND = 4

    def __init__(self, kind, td=None, ui=0, b0=False, b1=False, ir=False,
                 pir=False, p=None):
        self._kind = kind
        self._typedata = td
        self._paddingtype = p
        self._uintdata = ui
        self._booldata0 = b0
        self._booldata1 = b1
        self._inreg = ir
        self._paddinginreg = pir

    def __repr__(self):
        data = []
        if self.is_direct:
            data.append('Direct')
            data.append('coerce=%s' % self.coerce_to_type)
        elif self.is_indirect:
            data.append('Indirect')
            data.append('align=%s' % self.indirect_align)
            data.append('byval=%s' % self.indirect_by_val)
            data.append('realign=%s' % self.indirect_by_realign)
        elif self.is_extend:
            data.append('Extend')
        elif self.is_ignore:
            data.append('Ignore')
        elif self.is_expand:
            data.append('Expand')
        else:
            raise AssertionError('invalid kind: %s' % self._kind)

        return '<ArgInfo %s>' % ' '.join(data)

    # ---- accessors ----

    @property
    def is_direct(self):
        return self._kind == self.DIRECT

    @property
    def is_indirect(self):
        return self._kind == self.INDIRECT

    @property
    def is_extend(self):
        return self._kind == self.EXTEND

    @property
    def is_ignore(self):
        return self._kind == self.IGNORE

    @property
    def is_expand(self):
        return self._kind == self.EXPAND

    @property
    def can_have_coerce_to_type(self):
        return self.is_direct or self.is_extend

    @property
    def direct_offset(self):
        assert self.is_direct or self.is_extend
        return self._uintdata

    @property
    def padding_type(self):
        return self._paddingtype

    @property
    def padding_in_reg(self):
        return self._paddinginreg

    @property
    def coerce_to_type(self):
        assert self.can_have_coerce_to_type
        return self._typedata

    @coerce_to_type.setter
    def coerce_to_type(self, ty):
        self._typedata = ty

    @property
    def in_reg(self):
        return self.is_direct() or self.is_extend or self.is_indirect

    @property
    def indirect_align(self):
        assert self.is_indirect
        return self._uintdata

    @property
    def indirect_by_val(self):
        assert self.is_indirect
        return self._booldata0

    @property
    def indirect_by_realign(self):
        assert self.is_indirect
        return self._booldata1

    # ---- factories ----

    @classmethod
    def get_ignore(cls):
        return cls(kind=cls.IGNORE)

    @classmethod
    def get_extend(cls, ty=None):
        return cls(kind=cls.EXTEND, td=ty)

    @classmethod
    def get_direct(cls):
        return cls(kind=cls.DIRECT)

class ABIInfo(object):
    def __init__(self, datalayout):
        self.datalayout = datalayout

    def compute_info(self, return_type, args):
        self.return_info = self.classify_return_type(return_type)
        self.arg_infos = []
        for a in args:
            info = self.classify_argument_type(a)
            self.arg_infos.append(info)

    def classify_return_type(self, retty):
        raise NotImplementedError

    def classify_argument_type(self, argty):
        raise NotImplementedError

class DefaultABIInfo(ABIInfo):
    def classify_argument_type(self, argty):
        if argty.kind in AGGREGATE_TYPES:
            return ABIArgInfo.get_indirect()

        if self.promotable_integers(argty):
            return ABIArgInfo.get_extend()
        else:
            return ABIArgInfo.get_direct()

    def classify_return_type(self, retty):
        if retty.kind == lc.TYPE_VOID:
            return ABIArgInfo.get_ignore()

        if retty.kind in AGGREGATE_TYPES:
            return ABIArgInfo.get_indirect()

        if self.promotable_integers(retty):
            return ABIArgInfo.get_extend()
        else:
            return ABIArgInfo.get_direct()

    def promotable_integers(self, ty):
        if ty.kind != lc.TYPE_INTEGER:
            return False
        abisize = self.datalayout.abi_size(ty) * 8
        return ty.width < abisize

#------------------------------------------------------------------------------
# X86-32
#------------------------------------------------------------------------------

class X86_32ABIInfo(ABIInfo):
    MIN_ABI_STACK_ALIGN = 4    # bytes
