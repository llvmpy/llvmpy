#! /usr/bin/env python
# ______________________________________________________________________

from __future__ import absolute_import
import dis
import opcode

from .bytecode_visitor import BasicBlockVisitor
from . import opcode_util
from . import byte_control

# ______________________________________________________________________
# Class definition(s)

class BytecodeFlowBuilder (BasicBlockVisitor):
    '''Transforms a CFG into a bytecode "flow tree".

    The flow tree is a Python dictionary, described loosely by the
    following set of productions:

      * `flow_tree` ``:=`` ``{`` `blocks` ``*`` ``}``
      * `blocks` ``:=`` `block_index` ``:`` ``[`` `bytecode_tree` ``*`` ``]``
      * `bytecode_tree` ``:=`` ``(`` `opcode_index` ``,`` `opcode` ``,``
          `opname` ``,`` `arg` ``,`` ``[`` `bytecode_tree` ``*`` ``]`` ``)``

    The primary purpose of this transformation is to simulate the
    value stack, removing it and any stack-specific opcodes.'''

    def __init__ (self, *args, **kws):
        super(BytecodeFlowBuilder, self).__init__(*args, **kws)
        om_items = opcode_util.OPCODE_MAP.items()
        self.opmap = dict((opcode.opmap[opname], (opname, pops, pushes, stmt))
                          for opname, (pops, pushes, stmt) in om_items
                          if opname in opcode.opmap)

    def _visit_op (self, i, op, arg, opname, pops, pushes, appends):
        assert pops is not None, ('%s not well defined in opcode_util.'
                                  'OPCODE_MAP' % opname)
        if pops:
            if pops < 0:
                pops = arg - pops - 1
            assert pops <= len(self.stack), ("Stack underflow at instruction "
                                             "%d (%s)!" % (i, opname))
            stk_args = self.stack[-pops:]
            del self.stack[-pops:]
        else:
            stk_args = []
        ret_val = (i, op, opname, arg, stk_args)
        if pushes:
            self.stack.append(ret_val)
        if appends:
            self.block.append(ret_val)
        return ret_val

    def _op (self, i, op, arg):
        opname, pops, pushes, appends = self.opmap[op]
        return self._visit_op(i, op, arg, opname, pops, pushes, appends)

    def visit_cfg (self, cfg):
        self.cfg = cfg
        ret_val = self.visit(cfg.blocks)
        del self.cfg
        return ret_val

    def enter_blocks (self, blocks):
        labels = list(blocks.keys())
        labels.sort()
        self.blocks = dict((index, [])
                           for index in labels)
        self.control_stack = []
        self.stacks = {}

    def exit_blocks (self, blocks):
        ret_val = self.blocks
        del self.stacks
        del self.control_stack
        del self.blocks
        return ret_val

    def enter_block (self, block):
        self.block_no = block
        self.block = self.blocks[block]
        in_blocks = self.cfg.blocks_in[block]
        if len(in_blocks) == 0:
            self.stack = []
        else:
            pred_stack = None
            for pred in in_blocks:
                if pred in self.stacks:
                    pred_stack = self.stacks[pred]
                    break
            if pred_stack is not None:
                self.stack = pred_stack[:]
            else:
                raise NotImplementedError()

    def exit_block (self, block):
        assert self.block_no == block
        self.stacks[block] = self.stack
        del self.stack
        del self.block
        del self.block_no

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

    def op_BREAK_LOOP (self, i, op, arg):
        if self.opnames[op] == 'BREAK_LOOP':
            # Break target was already computed in control flow analysis;
            # reuse that, replacing the opcode argument.
            blocks_out = tuple(self.cfg.blocks_out[self.block_no])
            assert len(blocks_out) == 1
            assert arg is None
            arg = blocks_out[0]
        # else: Continue target is already in the argument.  Note that
        # the argument might not be the same as CFG destination block,
        # since we might have a finally block to visit first.
        return self._op(i, op, arg)

    op_BUILD_CLASS = _op
    op_BUILD_LIST = _op
    op_BUILD_MAP = _op
    op_BUILD_SLICE = _op
    op_BUILD_TUPLE = _op
    op_CALL_FUNCTION = _op
    op_CALL_FUNCTION_KW = _op
    op_CALL_FUNCTION_VAR = _op
    op_CALL_FUNCTION_VAR_KW = _op
    op_COMPARE_OP = _op
    op_CONTINUE_LOOP = op_BREAK_LOOP
    op_DELETE_ATTR = _op
    op_DELETE_FAST = _op
    op_DELETE_GLOBAL = _op
    op_DELETE_NAME = _op
    op_DELETE_SLICE = _op
    op_DELETE_SUBSCR = _op

    def op_DUP_TOP (self, i, op, arg):
        self.stack.append(self.stack[-1])

    def op_DUP_TOPX (self, i, op, arg):
        self.stack += self.stack[-arg:]

    #op_DUP_TOP_TWO = _not_implemented

    # See the note regarding END_FINALLY in the definition of
    # opcope_util.OPCODE_MAP.
    op_END_FINALLY = _op

    op_EXEC_STMT = _op

    def op_EXTENDED_ARG (self, i, op, arg):
        raise ValueError("Unexpected EXTENDED_ARG opcode at index %d (should "
                         "be removed by itercode)." % i)

    op_FOR_ITER = _op
    op_GET_ITER = _op

    def op_IMPORT_FROM (self, i, op, arg):
        # References top of stack without popping, so we can't use the
        # generic machinery.
        opname = self.opmap[op][0]
        ret_val = i, op, opname, arg, [self.stack[-1]]
        self.stack.append(ret_val)
        return ret_val

    op_IMPORT_NAME = _op
    op_IMPORT_STAR = _op
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
    op_JUMP_ABSOLUTE = _op
    op_JUMP_FORWARD = _op

    def op_JUMP_IF_FALSE (self, i, op, arg):
        ret_val = i, op, self.opnames[op], arg, [self.stack[-1]]
        self.block.append(ret_val)
        return ret_val

    #op_JUMP_IF_FALSE_OR_POP = _not_implemented
    op_JUMP_IF_TRUE = op_JUMP_IF_FALSE
    #op_JUMP_IF_TRUE_OR_POP = op_JUMP_IF_FALSE_OR_POP

    def op_LIST_APPEND (self, i, op, arg):
        '''This method is used for both LIST_APPEND, and SET_ADD
        opcodes.'''
        elem = self.stack.pop()
        container = self.stack[-arg]
        ret_val = i, op, self.opnames[op], arg, [container, elem]
        self.block.append(ret_val)
        return ret_val

    op_LOAD_ATTR = _op
    #op_LOAD_BUILD_CLASS = _not_implemented
    #op_LOAD_CLOSURE = _not_implemented
    op_LOAD_CONST = _op
    op_LOAD_DEREF = _op
    op_LOAD_FAST = _op
    op_LOAD_GLOBAL = _op
    op_LOAD_LOCALS = _op
    op_LOAD_NAME = _op
    op_MAKE_CLOSURE = _op
    op_MAKE_FUNCTION = _op
    op_NOP = _op

    def op_POP_BLOCK (self, i, op, arg):
        _, _, _, target_stack_size = self.control_stack.pop()
        pops = len(self.stack) - target_stack_size
        return self._visit_op(i, op, arg, self.opnames[op], pops, 0, 1)

    op_POP_JUMP_IF_FALSE = _op
    op_POP_JUMP_IF_TRUE = _op
    op_POP_TOP = _op
    op_PRINT_EXPR = _op
    op_PRINT_ITEM = _op
    op_PRINT_ITEM_TO = _op
    op_PRINT_NEWLINE = _op
    op_PRINT_NEWLINE_TO = _op
    op_RAISE_VARARGS = _op
    op_RETURN_VALUE = _op

    def op_ROT_FOUR (self, i, op, arg):
        self.stack[-4:] = (self.stack[-1], self.stack[-4], self.stack[-3],
                           self.stack[-2])

    def op_ROT_THREE (self, i, op, arg):
        self.stack[-3:] = (self.stack[-1], self.stack[-3], self.stack[-2])

    def op_ROT_TWO (self, i, op, arg):
        self.stack[-2:] = (self.stack[-1], self.stack[-2])

    def _op_SETUP (self, i, op, arg):
        self.control_stack.append((i, op, arg, len(self.stack)))
        ret_val = i, op, self.opnames[op], arg, []
        self.block.append(ret_val)
        return ret_val

    op_SETUP_EXCEPT = _op_SETUP
    op_SETUP_FINALLY = _op_SETUP
    op_SETUP_LOOP = _op_SETUP

    def op_SETUP_WITH (self, i, op, arg):
        assert arg is not None
        # Care has to be taken here.  SETUP_WITH pushes two things on
        # the value stack (the exit ), and once on the handler frame.
        ctx = self.stack.pop()
        # We signal that the value is an exit handler by setting arg to None
        exit_handler = i, op, self.opnames[op], None, [ctx]
        self.stack.append(exit_handler)
        ret_val = i, op, self.opnames[op], arg, [ctx]
        self.control_stack.append((i, op, arg, len(self.stack)))
        self.stack.append(ret_val)
        self.block.append(ret_val)
        return ret_val

    op_SET_ADD = op_LIST_APPEND
    op_SLICE = _op
    #op_STOP_CODE = _not_implemented
    op_STORE_ATTR = _op
    op_STORE_DEREF = _op
    op_STORE_FAST = _op
    op_STORE_GLOBAL = _op
    #op_STORE_LOCALS = _not_implemented
    op_STORE_MAP = _op
    op_STORE_NAME = _op
    op_STORE_SLICE = _op
    op_STORE_SUBSCR = _op
    op_UNARY_CONVERT = _op
    op_UNARY_INVERT = _op
    op_UNARY_NEGATIVE = _op
    op_UNARY_NOT = _op
    op_UNARY_POSITIVE = _op
    #op_UNPACK_EX = _not_implemented
    #op_UNPACK_SEQUENCE = _not_implemented
    #op_WITH_CLEANUP = _not_implemented
    op_YIELD_VALUE = _op

    @classmethod
    def build_flow(cls, func):
        '''Given a Python function, return a flow representation of that
        function.'''
        cfg = byte_control.build_cfg(func)
        return cls().visit_cfg(cfg)

    @classmethod
    def build_flow_from_co(cls, code_obj):
        '''Given a Python code object, return a flow representation of
        that code object.'''
        bbs = opcode_util.build_basic_blocks(code_obj)
        cfg = byte_control.ControlFlowBuilder().visit(bbs,
                                                      code_obj.co_argcount)
        return cls().visit_cfg(cfg)

    @classmethod
    def build_flows_from_co(cls, root_code_obj):
        '''Given a Python code object, return a map from that code
        object and any nested code objects to flow representations of
        those code objects.'''
        return dict((co, cls.build_flow_from_co(co))
                    for co in opcode_util.itercodeobjs(root_code_obj))

# ______________________________________________________________________
# Function definition(s)

def build_flow(func):
    '''Kept for backwards compatibility in downstream modules.  Use
    BytecodeFlowBuilder.build_flow() instead.'''
    return BytecodeFlowBuilder.build_flow(func)

# ______________________________________________________________________

def demo_flow_builder(builder_cls, *args):
    import pprint
    try:
        from .tests import llfuncs
    except ImportError:
        llfuncs = object()
    if not args:
        args = ('pymod',)
    for arg in args:
        if arg.endswith('.py'):
            with open(arg) as in_file:
                in_source = in_file.read()
                in_codeobj = compile(in_source, arg, 'exec')
                for codeobj in opcode_util.itercodeobjs(in_codeobj):
                    print("_" * 70)
                    print(codeobj)
                    pprint.pprint(builder_cls.build_flow_from_co(codeobj))
        else:
            pprint.pprint(builder_cls.build_flow(getattr(llfuncs, arg)))

# ______________________________________________________________________
# Main (self-test) routine

def main(*args):
    return demo_flow_builder(BytecodeFlowBuilder, *args)

# ______________________________________________________________________

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of byte_flow.py
