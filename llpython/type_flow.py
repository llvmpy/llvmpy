#! /usr/bin/env python
# ______________________________________________________________________
# Module imports

from .bytecode_visitor import BasicBlockVisitor, BenignBytecodeVisitorMixin

DEBUG_SIMPLIFY = False

if DEBUG_SIMPLIFY:
    from pprint import pprint as pp

# ______________________________________________________________________
# Class definition(s)

class TypeFlowBuilder(BenignBytecodeVisitorMixin, BasicBlockVisitor):
    def __init__(self, co_obj, *args, **kws):
        super(TypeFlowBuilder, self).__init__(*args, **kws)
        self.co_obj = co_obj
        self.locals = {}
        self.globals = {}
        self.refs = {}
        self.type_flow = {}
        self.requirements = {}

    def get_type_eqns(self):
        return self.type_flow, self.requirements, self.locals, self.globals

    def simplify(self):
        """
        This method isn't working as intended.  It should simplify
        strongly connected components s.t. instead of outputing
        several types like the following:

        {0: set(['in0']),
        3: set(['in1']),
        ...
        10: set([0, 3, 34, 37, 62, 65, 'in0', 'in1']),
        ...
        34: set([0, 3, 34, 37, 62, 65, 'in0', 'in1']),
        37: set(['in1']),
        ...
        62: set([0, 3, 34, 37, 62, 65, 'in0', 'in1']),
        65: set(['in1']),
        ...
        75: set([0, 3, 34, 37, 62, 65, 'in0', 'in1']),
        ...}

        It outputs the following:

        {0: set(['in0']),
        3: set(['in1']),
        ...
        10: set(['in0', 'in1']),
        ...
        34: set(['in0', 'in1']),
        37: set(['in1']),
        ...
        62: set(['in0', 'in1']),
        65: set(['in1']),
        ...
        75: set(['in0', 'in1']),
        ...}
        """
        if not DEBUG_SIMPLIFY:
            raise NotImplementedError("See docstring.")
        type_flow = self.type_flow
        changed = True
        while changed:
            changed = False
            next_flow = type_flow.copy()
            for index, types in type_flow.items():
                if isinstance(types, set):
                    next_types = set.union(
                        *(type_flow.get(child_index,
                                        set([child_index]))
                          for child_index in types))
                else:
                    next_types = set([types])
                if next_types != types:
                    next_flow[index] = next_types
                    changed = True
            pp(next_flow)
            print()
            type_flow = next_flow
        return type_flow

    def _op(self, i, op, opname, arg, args, *extras, **kws):
        self.type_flow[i] = set(args)

    op_BINARY_ADD = _op
    op_BINARY_AND = _op
    op_BINARY_DIVIDE = _op
    op_BINARY_FLOOR_DIVIDE = _op
    op_BINARY_LSHIFT = _op
    op_BINARY_MODULO = _op
    op_BINARY_MULTIPLY = _op
    op_BINARY_OR = _op
    op_BINARY_POWER = _op
    op_BINARY_RSHIFT = _op
    op_BINARY_SUBSCR = _op
    op_BINARY_SUBTRACT = _op
    op_BINARY_TRUE_DIVIDE = _op
    op_BINARY_XOR = _op

    #op_BUILD_CLASS = _do_nothing
    #op_BUILD_LIST = _do_nothing
    #op_BUILD_MAP = _do_nothing
    #op_BUILD_SET = _do_nothing
    #op_BUILD_SLICE = _do_nothing
    #op_BUILD_TUPLE = _do_nothing

    #op_CALL_FUNCTION = _do_nothing
    #op_CALL_FUNCTION_KW = _do_nothing
    #op_CALL_FUNCTION_VAR = _do_nothing
    #op_CALL_FUNCTION_VAR_KW = _do_nothing

    def op_COMPARE_OP(self, i, op, opname, arg, args, *extras, **kws):
        self.requirements[i] = set(args)
        self.type_flow[i] = bool

    #op_CONTINUE_LOOP = _do_nothing
    #op_DELETE_ATTR = _do_nothing
    #op_DELETE_DEREF = _do_nothing
    #op_DELETE_FAST = _do_nothing
    #op_DELETE_GLOBAL = _do_nothing
    #op_DELETE_NAME = _do_nothing
    #op_DELETE_SLICE = _do_nothing
    #op_DELETE_SUBSCR = _do_nothing
    #op_END_FINALLY = _do_nothing
    #op_EXEC_STMT = _do_nothing
    #op_EXTENDED_ARG = _do_nothing
    #op_FOR_ITER = _do_nothing
    #op_GET_ITER = _do_nothing
    #op_IMPORT_FROM = _do_nothing
    #op_IMPORT_NAME = _do_nothing
    #op_IMPORT_STAR = _do_nothing

    op_INPLACE_ADD = _op
    op_INPLACE_AND = _op
    op_INPLACE_DIVIDE = _op
    op_INPLACE_FLOOR_DIVIDE = _op
    op_INPLACE_LSHIFT = _op
    op_INPLACE_MODULO = _op
    op_INPLACE_MULTIPLY = _op
    op_INPLACE_OR = _op
    op_INPLACE_POWER = _op
    op_INPLACE_RSHIFT = _op
    op_INPLACE_SUBTRACT = _op
    op_INPLACE_TRUE_DIVIDE = _op
    op_INPLACE_XOR = _op

    #op_JUMP_ABSOLUTE = _do_nothing
    #op_JUMP_FORWARD = _do_nothing
    #op_JUMP_IF_FALSE = _do_nothing
    #op_JUMP_IF_FALSE_OR_POP = _do_nothing
    #op_JUMP_IF_TRUE = _do_nothing
    #op_JUMP_IF_TRUE_OR_POP = _do_nothing
    #op_LIST_APPEND = _do_nothing
    #op_LOAD_ATTR = _do_nothing
    #op_LOAD_BUILD_CLASS = _do_nothing
    #op_LOAD_CLOSURE = _do_nothing

    def op_LOAD_CONST(self, i, op, opname, arg, args, *extras, **kws):
        self.type_flow[i] = type(self.co_obj.co_consts[arg])

    def op_LOAD_DEREF(self, i, op, opname, arg, args, *extras, **kws):
        if arg not in self.refs:
            result = set(('inref%d' % arg,))
            self.refs[arg] = result
        else:
            result = self.refs[arg]
        self.type_flow[i] = result

    def op_LOAD_FAST(self, i, op, opname, arg, args, *extras, **kws):
        if arg not in self.locals:
            if arg < self.co_obj.co_argcount:
                result = set(('in%d' % arg,))
            else:
                result = set()
            self.locals[arg] = result
        else:
            result = self.locals[arg]
        self.type_flow[i] = result

    def op_LOAD_GLOBAL(self, i, op, opname, arg, args, *extras, **kws):
        if arg not in self.globals:
            result = set(('in%d' % arg,))
            self.globals[arg] = result
        else:
            result = self.globals[arg]
        self.type_flow[i] = result

    #op_LOAD_LOCALS = _do_nothing
    #op_LOAD_NAME = _do_nothing
    #op_MAKE_CLOSURE = _do_nothing
    #op_MAKE_FUNCTION = _do_nothing
    #op_MAP_ADD = _do_nothing
    #op_NOP = _do_nothing
    #op_POP_BLOCK = _do_nothing
    #op_POP_EXCEPT = _do_nothing
    #op_POP_JUMP_IF_FALSE = _do_nothing
    #op_POP_JUMP_IF_TRUE = _do_nothing
    #op_POP_TOP = _do_nothing
    #op_PRINT_EXPR = _do_nothing
    #op_PRINT_ITEM = _do_nothing
    #op_PRINT_ITEM_TO = _do_nothing
    #op_PRINT_NEWLINE = _do_nothing
    #op_PRINT_NEWLINE_TO = _do_nothing
    #op_RAISE_VARARGS = _do_nothing

    op_RETURN_VALUE = _op

    #op_SETUP_EXCEPT = _do_nothing
    #op_SETUP_FINALLY = _do_nothing
    #op_SETUP_LOOP = _do_nothing
    #op_SETUP_WITH = _do_nothing
    #op_SET_ADD = _do_nothing

    #op_SLICE = _do_nothing

    #op_STOP_CODE = _do_nothing
    #op_STORE_ATTR = _do_nothing
    #op_STORE_DEREF = _do_nothing

    def op_STORE_FAST(self, i, op, opname, arg, args, *extras, **kws):
        if arg not in self.locals:
            if arg < self.co_obj.co_argcount:
                result = set(('in%d' % arg,))
            else:
                result = set()
            self.locals[arg] = result
        else:
            result = self.locals[arg]
        assert len(args) == 1
        result.add(args[0])

    #op_STORE_GLOBAL = _do_nothing
    #op_STORE_LOCALS = _do_nothing
    #op_STORE_MAP = _do_nothing
    #op_STORE_NAME = _do_nothing
    #op_STORE_SLICE = _do_nothing
    #op_STORE_SUBSCR = _do_nothing

    op_UNARY_CONVERT = _op
    op_UNARY_INVERT = _op
    op_UNARY_NEGATIVE = _op
    op_UNARY_NOT = _op
    op_UNARY_POSITIVE = _op

    #op_UNPACK_EX = _do_nothing
    #op_UNPACK_SEQUENCE = _do_nothing
    #op_WITH_CLEANUP = _do_nothing
    #op_YIELD_VALUE = _do_nothing

# ______________________________________________________________________
# Function definition(s)

def build_type_flow(func):
    from .opcode_util import get_code_object
    from .addr_flow import build_addr_flow
    blocks = build_addr_flow(func)
    ty_builder = TypeFlowBuilder(get_code_object(func))
    ty_builder.visit(blocks)
    return ty_builder.get_type_eqns()

# ______________________________________________________________________
# Main (self-test) routine

def main(*args):
    import pprint
    from .tests import llfuncs
    if not args:
        args = ('pymod',)
    for arg in args:
        pprint.pprint(build_type_flow(getattr(llfuncs, arg)))

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of type_flow.py
