#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ______________________________________________________________________
# Module imports

from __future__ import print_function, division, absolute_import

import inspect

import llvm.core as lc

from . import byte_control
from . import addr_flow
from . import opcode_util
from . import bytetype
from .bytecode_visitor import GenericFlowVisitor

# ______________________________________________________________________
# Class definitions

class AddressFlowToLLVMPyAPICalls(GenericFlowVisitor):

    def __init__(self, _prefix=None, _postfix=None):
        if _prefix is not None:
            if inspect.isfunction(_prefix):
                __prefix = _prefix
            else:
                def __prefix(self, opname, *opargs):
                    return _prefix
            self.prefix = __prefix
        if _postfix is not None:
            if inspect.isfunction(_postfix):
                __postfix = _postfix
            else:
                def __postfix(self, opname, *opargs):
                    return _postfix
            self.postfix = __postfix

    def prefix(self, opname, *opargs):
        return ''

    def postfix(self, opname, *opargs):
        return ''

    def translate_cfg(self, code_obj, cfg, llvm_module=None, **kws):
        assert inspect.iscode(code_obj)
        self.code_obj = code_obj
        self.cfg = cfg
        self.target_function_name = kws.get(
            'target_function_name', 'co_%s_%x' % (code_obj.co_name,
                                                  id(code_obj)))
        if llvm_module is None:
            llvm_module = lc.Module.new('lmod_' + self.target_function_name)
        self.llvm_module = llvm_module
        self.visit(cfg.blocks)
        del self.llvm_module
        del self.cfg
        del self.code_obj
        return llvm_module

    def enter_flow_object(self, flow):
        super(AddressFlowToLLVMPyAPICalls, self).enter_flow_object(flow)
        self.nargs = opcode_util.get_nargs(self.code_obj)
        lltype = lc.Type.function(bytetype.l_pyobj_p,
                                  tuple(bytetype.l_pyobj_p
                                        for _ in range(self.nargs)))
        self.llvm_function = self.llvm_module.add_function(
            lltype, self.target_function_name)
        self.llvm_blocks = {}
        for block in self.block_list:
            if 0 in self.cfg.blocks_reaching[block]:
                bb = self.llvm_function.append_basic_block(
                    'BLOCK_%d' % (block,))
                self.llvm_blocks[block] = bb

    def exit_flow_object(self, flow):
        super(AddressFlowToLLVMPyAPICalls, self).exit_flow_object(flow)
        del self.llvm_blocks
        del self.llvm_function

    def enter_block(self, block):
        ret_val = False
        if block in self.llvm_blocks:
            self.llvm_block = self.llvm_blocks[block]
            self.builder = lc.Builder.new(self.llvm_block)
            ret_val = True
        return ret_val

    def exit_block(self, block):
        # XXX Isn't this really a bug in GenericFlowVisitor.visit()?
        if block in self.llvm_blocks:
            del self.builder
            del self.llvm_block

    def _op(self, i, op, arg, *args, **kws):
        return[]
        raise NotImplementedError()

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
    op_BREAK_LOOP = _op
    op_BUILD_CLASS = _op
    op_BUILD_LIST = _op
    op_BUILD_MAP = _op
    op_BUILD_SET = _op
    op_BUILD_SLICE = _op
    op_BUILD_TUPLE = _op
    op_CALL_FUNCTION = _op
    op_CALL_FUNCTION_KW = _op
    op_CALL_FUNCTION_VAR = _op
    op_CALL_FUNCTION_VAR_KW = _op
    op_COMPARE_OP = _op
    op_CONTINUE_LOOP = _op
    op_DELETE_ATTR = _op
    op_DELETE_DEREF = _op
    op_DELETE_FAST = _op
    op_DELETE_GLOBAL = _op
    op_DELETE_NAME = _op
    op_DELETE_SLICE = _op
    op_DELETE_SUBSCR = _op
    op_DUP_TOP = _op
    op_DUP_TOPX = _op
    op_DUP_TOP_TWO = _op
    op_END_FINALLY = _op
    op_EXEC_STMT = _op
    op_EXTENDED_ARG = _op
    op_FOR_ITER = _op
    op_GET_ITER = _op
    op_IMPORT_FROM = _op
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
    op_JUMP_IF_FALSE = _op
    op_JUMP_IF_FALSE_OR_POP = _op
    op_JUMP_IF_TRUE = _op
    op_JUMP_IF_TRUE_OR_POP = _op
    op_LIST_APPEND = _op
    op_LOAD_ATTR = _op
    op_LOAD_BUILD_CLASS = _op
    op_LOAD_CLOSURE = _op
    op_LOAD_CONST = _op
    op_LOAD_DEREF = _op
    op_LOAD_FAST = _op
    op_LOAD_GLOBAL = _op
    op_LOAD_LOCALS = _op
    op_LOAD_NAME = _op
    op_MAKE_CLOSURE = _op
    op_MAKE_FUNCTION = _op
    op_MAP_ADD = _op
    op_NOP = _op
    op_POP_BLOCK = _op
    op_POP_EXCEPT = _op
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
    op_ROT_FOUR = _op
    op_ROT_THREE = _op
    op_ROT_TWO = _op
    op_SETUP_EXCEPT = _op
    op_SETUP_FINALLY = _op
    op_SETUP_LOOP = _op
    op_SETUP_WITH = _op
    op_SET_ADD = _op
    op_SLICE = _op
    op_STOP_CODE = _op
    op_STORE_ATTR = _op
    op_STORE_DEREF = _op
    op_STORE_FAST = _op
    op_STORE_GLOBAL = _op
    op_STORE_LOCALS = _op
    op_STORE_MAP = _op
    op_STORE_NAME = _op
    op_STORE_SLICE = _op
    op_STORE_SUBSCR = _op
    op_UNARY_CONVERT = _op
    op_UNARY_INVERT = _op
    op_UNARY_NEGATIVE = _op
    op_UNARY_NOT = _op
    op_UNARY_POSITIVE = _op
    op_UNPACK_EX = _op
    op_UNPACK_SEQUENCE = _op
    op_WITH_CLEANUP = _op
    op_YIELD_VALUE = _op

# ______________________________________________________________________
# Function definition(s)

def demo_translator(*args, **kws):
    def _visit(obj):
        if inspect.isfunction(obj):
            obj = opcode_util.get_code_object(obj)
        print('\n; %s\n; %r' % ('_' * 70, obj))
        cfg = byte_control.ControlFlowBuilder.build_cfg_from_co(obj)
        cfg.blocks = addr_flow.AddressFlowBuilder().visit_cfg(cfg)
        print(AddressFlowToLLVMPyAPICalls(**kws).translate_cfg(obj, cfg))
    return opcode_util.visit_code_args(_visit, *args)

# ______________________________________________________________________
# Main (self-test) routine

if __name__ == '__main__':
    import sys
    demo_translator(*sys.argv[1:], _prefix = '_')

# ______________________________________________________________________
# End of af_to_api.py
