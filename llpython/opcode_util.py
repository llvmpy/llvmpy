#! /usr/bin/env python
# ______________________________________________________________________

from collections import namedtuple
import dis
import opcode
import types

# ______________________________________________________________________
# Module data

# Note that opcode.hasjrel and opcode.hasjabs applies only to opcodes
# that calculate a jump point based on the argument.  This ignores
# jumps that use the frame stack to calculate their targets, and
# exceptions.

NON_ARG_JUMP_NAMES = ('BREAK_LOOP', 'RETURN_VALUE', 'END_FINALLY',
                      'RAISE_VARARGS')
NON_ARG_JUMPS = [opcode.opmap[opname]
                 for opname in NON_ARG_JUMP_NAMES
                 if opname in opcode.opmap]
HAS_CBRANCH_NAMES = 'FOR_ITER',
hasjump = opcode.hasjrel + opcode.hasjabs + NON_ARG_JUMPS
hascbranch = [op for op, opname in ((op, opcode.opname[op])
                                    for op in hasjump)
              if 'IF' in opname
              or 'SETUP' in opname
              or opname in HAS_CBRANCH_NAMES]

OpcodeData = namedtuple('OpcodeData', ('pops', 'pushes', 'is_stmt'))
NO_OPCODE_DATA = OpcodeData(None, None, None)

# Since the actual opcode value may change, manage opcode abstraction
# data by opcode name.

OPCODE_MAP = {
    'BINARY_ADD': OpcodeData(2, 1, None),
    'BINARY_AND': OpcodeData(2, 1, None),
    'BINARY_DIVIDE': OpcodeData(2, 1, None),
    'BINARY_FLOOR_DIVIDE': OpcodeData(2, 1, None),
    'BINARY_LSHIFT': OpcodeData(2, 1, None),
    'BINARY_MODULO': OpcodeData(2, 1, None),
    'BINARY_MULTIPLY': OpcodeData(2, 1, None),
    'BINARY_OR': OpcodeData(2, 1, None),
    'BINARY_POWER': OpcodeData(2, 1, None),
    'BINARY_RSHIFT': OpcodeData(2, 1, None),
    'BINARY_SUBSCR': OpcodeData(2, 1, None),
    'BINARY_SUBTRACT': OpcodeData(2, 1, None),
    'BINARY_TRUE_DIVIDE': OpcodeData(2, 1, None),
    'BINARY_XOR': OpcodeData(2, 1, None),
    'BREAK_LOOP': OpcodeData(0, None, 1),
    'BUILD_CLASS': OpcodeData(3, 1, None),
    'BUILD_LIST': OpcodeData(-1, 1, None),
    'BUILD_MAP': OpcodeData(-1, 1, None),
    'BUILD_SET': OpcodeData(-1, 1, None),
    'BUILD_SLICE': OpcodeData(-1, 1, None), # oparg should only be 2 or 3
    'BUILD_TUPLE': OpcodeData(-1, 1, None),
    'CALL_FUNCTION': OpcodeData(-2, 1, None),
    'CALL_FUNCTION_KW': OpcodeData(-3, 1, None),
    'CALL_FUNCTION_VAR': OpcodeData(-3, 1, None),
    'CALL_FUNCTION_VAR_KW': OpcodeData(-4, 1, None),
    'COMPARE_OP': OpcodeData(2, 1, None),
    'CONTINUE_LOOP': OpcodeData(0, None, 1),
    'DELETE_ATTR': OpcodeData(1, None, 1),
    'DELETE_DEREF': NO_OPCODE_DATA,
    'DELETE_FAST': OpcodeData(0, None, 1),
    'DELETE_GLOBAL': OpcodeData(0, None, 1),
    'DELETE_NAME': OpcodeData(0, None, 1),
    'DELETE_SLICE+0': OpcodeData(1, None, 1),
    'DELETE_SLICE+1': OpcodeData(2, None, 1),
    'DELETE_SLICE+2': OpcodeData(2, None, 1),
    'DELETE_SLICE+3': OpcodeData(3, None, 1),
    'DELETE_SUBSCR': OpcodeData(2, None, 1),
    'DUP_TOP': NO_OPCODE_DATA,
    'DUP_TOPX': NO_OPCODE_DATA,
    'DUP_TOP_TWO': NO_OPCODE_DATA,

    # The data for END_FINALLY is a total fabrication; END_FINALLY may
    # pop 1 or 3 values off the value stack, based on the type of the
    # top of the value stack.  If, however, a value stack simulator
    # ignores the part of the CPython evaluator loop that pushes the
    # why code on the value stack for WHY_RETURN and WHY_CONTINUE (as
    # this table does), this should work out fine.
    'END_FINALLY': OpcodeData(0, 0, 1), 

    'EXEC_STMT': OpcodeData(3, 0, 1),
    'EXTENDED_ARG': NO_OPCODE_DATA,
    'FOR_ITER': OpcodeData(1, 1, 1),
    'GET_ITER': OpcodeData(1, 1, None),
    'IMPORT_FROM': NO_OPCODE_DATA,
    'IMPORT_NAME': OpcodeData(2, 1, None),
    'IMPORT_STAR': OpcodeData(1, None, 1),
    'INPLACE_ADD': OpcodeData(2, 1, None),
    'INPLACE_AND': OpcodeData(2, 1, None),
    'INPLACE_DIVIDE': OpcodeData(2, 1, None),
    'INPLACE_FLOOR_DIVIDE': OpcodeData(2, 1, None),
    'INPLACE_LSHIFT': OpcodeData(2, 1, None),
    'INPLACE_MODULO': OpcodeData(2, 1, None),
    'INPLACE_MULTIPLY': OpcodeData(2, 1, None),
    'INPLACE_OR': OpcodeData(2, 1, None),
    'INPLACE_POWER': OpcodeData(2, 1, None),
    'INPLACE_RSHIFT': OpcodeData(2, 1, None),
    'INPLACE_SUBTRACT': OpcodeData(2, 1, None),
    'INPLACE_TRUE_DIVIDE': OpcodeData(2, 1, None),
    'INPLACE_XOR': OpcodeData(2, 1, None),
    'JUMP_ABSOLUTE': OpcodeData(0, None, 1),
    'JUMP_FORWARD': OpcodeData(0, None, 1),
    'JUMP_IF_FALSE': OpcodeData(1, 1, 1),
    'JUMP_IF_FALSE_OR_POP': NO_OPCODE_DATA,
    'JUMP_IF_TRUE': OpcodeData(1, 1, 1),
    'JUMP_IF_TRUE_OR_POP': NO_OPCODE_DATA,
    'LIST_APPEND': NO_OPCODE_DATA,
    'LOAD_ATTR': OpcodeData(1, 1, None),
    'LOAD_BUILD_CLASS': NO_OPCODE_DATA,
    'LOAD_CLOSURE': NO_OPCODE_DATA,
    'LOAD_CONST': OpcodeData(0, 1, None),
    'LOAD_DEREF': OpcodeData(0, 1, None),
    'LOAD_FAST': OpcodeData(0, 1, None),
    'LOAD_GLOBAL': OpcodeData(0, 1, None),
    'LOAD_LOCALS': OpcodeData(0, 1, None),
    'LOAD_NAME': OpcodeData(0, 1, None),
    'MAKE_CLOSURE': NO_OPCODE_DATA,
    'MAKE_FUNCTION': OpcodeData(-2, 1, None),
    'MAP_ADD': NO_OPCODE_DATA,
    'NOP': OpcodeData(0, None, None),
    'POP_BLOCK': OpcodeData(0, None, 1),
    'POP_EXCEPT': NO_OPCODE_DATA,
    'POP_JUMP_IF_FALSE': OpcodeData(1, None, 1),
    'POP_JUMP_IF_TRUE': OpcodeData(1, None, 1),
    'POP_TOP': OpcodeData(1, None, 1),
    'PRINT_EXPR': OpcodeData(1, None, 1),
    'PRINT_ITEM': OpcodeData(1, None, 1),
    'PRINT_ITEM_TO': OpcodeData(2, None, 1),
    'PRINT_NEWLINE': OpcodeData(0, None, 1),
    'PRINT_NEWLINE_TO': OpcodeData(1, None, 1),
    'RAISE_VARARGS': OpcodeData(-1, None, 1),
    'RETURN_VALUE': OpcodeData(1, None, 1),
    'ROT_FOUR': NO_OPCODE_DATA,
    'ROT_THREE': NO_OPCODE_DATA,
    'ROT_TWO': NO_OPCODE_DATA,
    'SETUP_EXCEPT': NO_OPCODE_DATA,
    'SETUP_FINALLY': NO_OPCODE_DATA,
    'SETUP_LOOP': NO_OPCODE_DATA,
    'SETUP_WITH': NO_OPCODE_DATA,
    'SET_ADD': NO_OPCODE_DATA,
    'SLICE+0': OpcodeData(1, 1, None),
    'SLICE+1': OpcodeData(2, 1, None),
    'SLICE+2': OpcodeData(2, 1, None),
    'SLICE+3': OpcodeData(3, 1, None),
    'STOP_CODE': NO_OPCODE_DATA,
    'STORE_ATTR': OpcodeData(2, None, 1),
    'STORE_DEREF': OpcodeData(1, 0, 1),
    'STORE_FAST': OpcodeData(1, None, 1),
    'STORE_GLOBAL': OpcodeData(1, None, 1),
    'STORE_LOCALS': NO_OPCODE_DATA,
    'STORE_MAP': OpcodeData(1, None, 1),
    'STORE_NAME': OpcodeData(1, None, 1),
    'STORE_SLICE+0': OpcodeData(1, None, 1),
    'STORE_SLICE+1': OpcodeData(2, None, 1),
    'STORE_SLICE+2': OpcodeData(2, None, 1),
    'STORE_SLICE+3': OpcodeData(3, None, 1),
    'STORE_SUBSCR': OpcodeData(3, None, 1),
    'UNARY_CONVERT': OpcodeData(1, 1, None),
    'UNARY_INVERT': OpcodeData(1, 1, None),
    'UNARY_NEGATIVE': OpcodeData(1, 1, None),
    'UNARY_NOT': OpcodeData(1, 1, None),
    'UNARY_POSITIVE': OpcodeData(1, 1, None),
    'UNPACK_EX': NO_OPCODE_DATA,
    'UNPACK_SEQUENCE': NO_OPCODE_DATA,
    'WITH_CLEANUP': NO_OPCODE_DATA,
    'YIELD_VALUE': OpcodeData(1, None, 1),
}

# ______________________________________________________________________
# Module functions

def itercode(code, start = 0):
    """Return a generator of byte-offset, opcode, and argument
    from a byte-code-string
    """
    i = 0
    extended_arg = 0
    if isinstance(code[0], str):
        code = [ord(c) for c in code]
    n = len(code)
    while i < n:
        op = code[i]
        num = i + start
        i = i + 1
        oparg = None
        if op >= opcode.HAVE_ARGUMENT:
            oparg = code[i] + (code[i + 1] * 256) + extended_arg
            extended_arg = 0
            i = i + 2
            if op == opcode.EXTENDED_ARG:
                extended_arg = oparg * 65536
                continue

        delta = yield num, op, oparg
        if delta is not None:
            abs_rel, dst = delta
            assert abs_rel == 'abs' or abs_rel == 'rel'
            i = dst if abs_rel == 'abs' else i + dst

# ______________________________________________________________________

def itercodeobjs(codeobj):
    "Iterator that traverses code objects via the co_consts member."
    yield codeobj
    for const in codeobj.co_consts:
        if isinstance(const, types.CodeType):
            for childobj in itercodeobjs(const):
                yield childobj

# ______________________________________________________________________

def visit_code_args(visitor, *args, **kws):
    """Utility function for testing or demonstrating various code
    analysis passes in llpython.

    Takes a visitor function and a sequence of command line arguments.
    The visitor function should be able to handle either function
    objects or code objects."""
    try:
        from .tests import llfuncs
    except ImportError:
        llfuncs = object()
    if not args:
        if 'default_args' in kws:
            args = kws['default_args']
        else:
            args = ('pymod',)
    for arg in args:
        if arg.endswith('.py'):
            with open(arg) as in_file:
                in_source = in_file.read()
                in_codeobj = compile(in_source, arg, 'exec')
                for codeobj in itercodeobjs(in_codeobj):
                    visitor(codeobj)
        else:
            visitor(getattr(llfuncs, arg))

# ______________________________________________________________________

def extendlabels(code, labels = None):
    """Extend the set of jump target labels to account for the
    passthrough targets of conditional branches.

    This allows us to create a control flow graph where there is at
    most one branch per basic block.
    """
    if labels is None:
        labels = []
    if isinstance(code[0], str):
        code = [ord(c) for c in code]
    n = len(code)
    i = 0
    while i < n:
        op = code[i]
        i += 1
        if op >= dis.HAVE_ARGUMENT:
            i += 2
        if op in hasjump and i < n and i not in labels:
            labels.append(i)
    return labels

# ______________________________________________________________________

def get_code_object (func):
    return getattr(func, '__code__', getattr(func, 'func_code', None))

# ______________________________________________________________________

def build_basic_blocks (co_obj):
    co_code = co_obj.co_code
    labels = extendlabels(co_code, dis.findlabels(co_code))
    labels.sort()
    blocks = dict((index, list(itercode(co_code[index:next_index], index)))
                  for index, next_index in zip([0] + labels,
                                               labels + [len(co_code)]))
    return blocks

# ______________________________________________________________________
# End of opcode_util.py
