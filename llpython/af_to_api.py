#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ______________________________________________________________________
# Module imports

from __future__ import print_function, division, absolute_import

import inspect
import opcode

import llvm.core as lc

from . import byte_control
from . import addr_flow
from . import opcode_util
from .bytetype import l_pyobj_p, lc_int
from .bytecode_visitor import GenericFlowVisitor

# ______________________________________________________________________
# Class definitions

class AddressFlowToLLVMPyAPICalls(GenericFlowVisitor):
    '''
    Code generator for translating from a Python code object and its
    address flow (output by addr_flow.AddressFlowBuilder) into an LLVM
    function.  The resulting LLVM function calls into a user-provided
    (or undefined) API function for each interpreter byte code.

    Target API function names are based on a programmable name
    mangling scheme:

    <PREFIX>OPCODE_NAME<POSTFIX>

    The <PREFIX> and <POSTFIX> strings are determined by the prefix()
    and postfix() methods.  These methods may either be overloaded, or
    specialized at construction time using _prefix and _postfix
    arguments.  The OPCODE_NAME is the opcode name as determined by
    the map in opcode.opname.
    '''
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

    def get_op_function(self, opname, *opargs, **kwds):
        target_fn_ty = lc.Type.function(kwds.get('return_type', self.obj_type),
                                        [arg.type for arg in opargs])
        target_fn_name = ''.join((self.prefix(opname, *opargs), opname,
                                  self.postfix(opname, *opargs)))
        return self.llvm_module.get_or_insert_function(target_fn_ty,
                                                       target_fn_name)

    def translate_cfg(self, code_obj, cfg, llvm_module=None,
                      monotype = l_pyobj_p, **kws):
        '''
        Generate LLVM code for the given code object and it's control
        flow graph.

        If no LLVM module is given as an argument, translate_cfg()
        creates a new module.

        Returns the resulting LLVM module.
        '''
        assert inspect.iscode(code_obj)
        self.obj_type = monotype
        self.null = lc.Constant.null(self.obj_type)
        self.code_obj = code_obj
        self.cfg = cfg
        self.target_function_name = kws.get(
            'target_function_name', 'co_%s_%x' % (code_obj.co_name,
                                                  id(code_obj)))
        if llvm_module is None:
            llvm_module = lc.Module.new('lmod_' + self.target_function_name)
        self.llvm_module = llvm_module
        self.incref = self.get_op_function('INCREF', self.null)
        self.decref = self.get_op_function('DECREF', self.null,
                                           return_type = lc.Type.void())
        self.visit(cfg.blocks)
        del self.llvm_module
        del self.cfg
        del self.code_obj
        return llvm_module

    def enter_flow_object(self, flow):
        '''
        Set up any state for dealing a new dictionary of basic blocks.
        '''
        super(AddressFlowToLLVMPyAPICalls, self).enter_flow_object(flow)
        self.nargs = opcode_util.get_nargs(self.code_obj)
        lltype = lc.Type.function(
            self.obj_type, tuple(self.obj_type for _ in range(self.nargs)))
        self.llvm_function = self.llvm_module.add_function(
            lltype, self.target_function_name)
        self.llvm_blocks = {}
        for block in self.block_list:
            if 0 in self.cfg.blocks_reaching[block]:
                bb = self.llvm_function.append_basic_block(
                    'BLOCK_%d' % (block,))
                self.llvm_blocks[block] = bb
        self.symtab = {}
        self.values = {}

    def exit_flow_object(self, flow):
        '''
        Clean up any state created while visiting the given dictionary
        of basic blocks.
        '''
        super(AddressFlowToLLVMPyAPICalls, self).exit_flow_object(flow)
        del self.symtab
        del self.llvm_blocks
        del self.llvm_function

    def generate_co_init(self):
        '''
        Initialize the code object's local variables on the stack.
        '''
        for name in self.code_obj.co_varnames:
            ptr = self.builder.alloca(self.obj_type, name + '_p')
            self.symtab[name] = ptr
            self.builder.store(self.null, ptr)
        for arg_index, arg in zip(range(self.nargs), self.llvm_function.args):
            if arg_index == 0:
                arg.name = '_globals_%x' % id(self.code_obj)
                self.globals = arg
            else:
                local_index = arg_index - 1
                name = self.code_obj.co_varnames[local_index]
                arg.name = name
                self.builder.store(arg, self.symtab[name])

    def enter_block(self, block):
        '''
        Set up state for generating code in a new basic block.  If
        this is the first basic block, initialize the local variables
        using generate_co_init().
        '''
        ret_val = False
        if block in self.llvm_blocks:
            self.llvm_block = self.llvm_blocks[block]
            self.builder = lc.Builder.new(self.llvm_block)
            if block == 0:
                self.generate_co_init()
            ret_val = True
        return ret_val

    def exit_block(self, block):
        '''
        Tear down any state created for code generation in the current
        basic block.  If the basic block isn't already terminated by a
        control flow statement, assume it branches to the next basic
        block.
        '''
        # XXX Isn't this really a bug in GenericFlowVisitor.visit()?
        if block in self.llvm_blocks:
            bb_instrs = self.llvm_block.instructions
            if ((len(bb_instrs) == 0) or
                    (not bb_instrs[-1].is_terminator)):
                out_blocks = list(self.cfg.blocks_out[block])
                assert len(out_blocks) == 1, [str(i) for i in bb_instrs]
                self.builder.branch(self.llvm_blocks[out_blocks[0]])
            del self.builder
            del self.llvm_block

    def _op(self, i, op, arg, *args, **kws):
        args = [self.values[stkarg] for stkarg in args]
        if arg is not None:
            args.insert(0, lc.Constant.int(lc_int, arg))
        # XXX Modify the visitor!  Should be passing Instr named
        # tuples here, and not looking up the operation name.
        target_fn = self.get_op_function(self.opnames[op], *args, **kws)
        result = self.builder.call(target_fn, args)
        self.values[i] = result
        return [result]

    def _not_implemented(self, i, op, arg, *args, **kws):
        raise NotImplementedError(self.opnames[op])

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

    def op_JUMP_ABSOLUTE(self, i, op, arg, *args, **kws):
        return [self.builder.branch(self.llvm_blocks[arg])]

    def op_JUMP_FORWARD(self, i, op, arg, *args, **kws):
        return [self.builder.branch(self.llvm_blocks[i + arg + 3])]

    op_JUMP_IF_FALSE = _not_implemented
    op_JUMP_IF_FALSE_OR_POP = _not_implemented
    op_JUMP_IF_TRUE = _not_implemented
    op_JUMP_IF_TRUE_OR_POP = _not_implemented
    op_LIST_APPEND = _op
    op_LOAD_ATTR = _op
    op_LOAD_BUILD_CLASS = _op
    op_LOAD_CLOSURE = _op
    op_LOAD_CONST = _op
    op_LOAD_DEREF = _op

    def op_LOAD_FAST(self, i, op, arg, *args, **kws):
        varname = self.code_obj.co_varnames[arg]
        result = self.builder.load(self.symtab[varname])
        self.values[i] = result
        return [result, self.builder.call(self.incref, [result])]

    op_LOAD_GLOBAL = _op
    op_LOAD_LOCALS = _op
    op_LOAD_NAME = _op
    op_MAKE_CLOSURE = _op
    op_MAKE_FUNCTION = _op
    op_MAP_ADD = _op
    op_NOP = _op
    op_POP_BLOCK = _op
    op_POP_EXCEPT = _op

    def _op_cbranch(self, i, op, arg, *args, **kws):
        branch_taken = self.llvm_blocks[arg]
        branch_not_taken = self.llvm_blocks[i + 3]
        _kws = kws.copy()
        _kws.update(return_type=lc.Type.int(1))
        test = self._op(i, op, None, *args, **_kws)[0]
        return [test, self.builder.cbranch(test, branch_taken,
                                           branch_not_taken)]

    op_POP_JUMP_IF_FALSE = _op_cbranch
    op_POP_JUMP_IF_TRUE = _op_cbranch

    op_POP_TOP = _not_implemented
    op_PRINT_EXPR = _op
    op_PRINT_ITEM = _op
    op_PRINT_ITEM_TO = _op
    op_PRINT_NEWLINE = _op
    op_PRINT_NEWLINE_TO = _op
    op_RAISE_VARARGS = _op

    def op_RETURN_VALUE(self, i, op, arg, *args):
        return [self.builder.ret(self.values[args[0]])]

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

    def op_STORE_FAST(self, i, op, arg, *args):
        src_index, = args
        src = self.values[src_index]
        varname = self.code_obj.co_varnames[arg]
        result = self.builder.store(src, self.symtab[varname])
        self.values[i] = result
        return [result]

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
