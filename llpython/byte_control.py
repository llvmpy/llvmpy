#! /usr/bin/env python
# ______________________________________________________________________
from __future__ import absolute_import
import opcode
from . import opcode_util
import pprint

from .bytecode_visitor import BasicBlockVisitor, BenignBytecodeVisitorMixin
from .control_flow import ControlFlowGraph

# ______________________________________________________________________
# Module data

# The following opcodes branch based on the control (a.k.a. frame)
# stack:
RETURN_VALUE, CONTINUE_LOOP, BREAK_LOOP, END_FINALLY = (
    opcode.opmap[opname] for opname in (
        'RETURN_VALUE', 'CONTINUE_LOOP', 'BREAK_LOOP', 'END_FINALLY'))

# The following opcodes push a new frame on the control stack:
SETUP_EXCEPT, SETUP_FINALLY, SETUP_LOOP, SETUP_WITH = (
    opcode.opmap.get(opname, None) for opname in (
        'SETUP_EXCEPT', 'SETUP_FINALLY', 'SETUP_LOOP', 'SETUP_WITH'))

WHY_NOT = 1
WHY_EXCEPTION = WHY_NOT << 1
WHY_RERAISE = WHY_EXCEPTION << 1
WHY_RETURN = WHY_RERAISE << 1
WHY_BREAK = WHY_RETURN << 1
WHY_CONTINUE = WHY_BREAK << 1
WHY_YIELD = WHY_CONTINUE << 1

# ______________________________________________________________________
# Class definition(s)

class ControlFlowBuilder (BenignBytecodeVisitorMixin, BasicBlockVisitor):
    '''Visitor responsible for traversing a bytecode basic block map and
    building a control flow graph (CFG).

    The primary purpose of this transformation is to create a CFG,
    which is used by later transformers for dataflow analysis.
    '''
    def visit (self, flow, nargs = 0, *args, **kws):
        '''Given a bytecode flow, and an optional number of arguments,
        return a :py:class:`llpython.control_flow.ControlFlowGraph`
        instance describing the full control flow of the bytecode
        flow.'''
        self.nargs = nargs
        ret_val = super(ControlFlowBuilder, self).visit(flow, *args, **kws)
        del self.nargs
        return ret_val

    def enter_blocks (self, blocks):
        super(ControlFlowBuilder, self).enter_blocks(blocks)
        self.blocks = blocks
        self.block_list = list(blocks.keys())
        self.block_list.sort()
        self.cfg = ControlFlowGraph()
        self.control_stack = []
        for block in self.block_list:
            self.cfg.add_block(block, blocks[block])

    def exit_blocks (self, blocks):
        super(ControlFlowBuilder, self).exit_blocks(blocks)
        assert self.blocks == blocks
        self.cfg.compute_dataflow()
        self.cfg.update_for_ssa()
        ret_val = self.cfg
        del self.control_stack
        del self.cfg
        del self.block_list
        del self.blocks
        return ret_val

    def enter_block (self, block):
        self.block = block
        assert block in self.cfg.blocks
        if block == 0:
            for local_index in range(self.nargs):
                self.op_STORE_FAST(0, opcode.opmap['STORE_FAST'], local_index)
        return True

    def _get_next_block (self, block):
        return self.block_list[self.block_list.index(block) + 1]

    def _generate_handler_edge (self, block, i, op, arg, why):
        """Given a reason (corresponding to the why code in
        Python/ceval.c), interrupt control flow, possibly using the
        control flow (a.k.a. frame) stack to calculate the next
        target.

        Returns True if an edge was added to the CFG, False otherwise.
        Based on the opcode the return result may mean different
        things (for example: if why == WHY_RETURN, then the function
        returns)."""
        ret_val = False
        if len(self.control_stack) > 0:
            handlers = set((SETUP_FINALLY, SETUP_WITH))
            if why == WHY_EXCEPTION:
                handlers.add(SETUP_EXCEPT)
            reverse_stack = self.control_stack[::-1]
            target = None
            for handler_i, handler_op, handler_arg in reverse_stack:
                if handler_op in handlers:
                    target = handler_i + handler_arg + 3
                elif handler_op == SETUP_LOOP:
                    if why == WHY_CONTINUE:
                        if op == CONTINUE_LOOP:
                            target = i + arg + 3
                        else:
                            # XXX This isn't going to be correct for
                            # for-loops, or really long while-loops
                            # (which use EXTENDED_ARG):
                            target = handler_i + 3
                    elif why == WHY_BREAK:
                        target = handler_i + handler_arg + 3
                if target is not None:
                    self.cfg.add_edge(block, target)
                    ret_val = True
                    break
        return ret_val

    def exit_block (self, block):
        assert block == self.block
        del self.block
        i, op, arg = self.blocks[block][-1]
        goto_next = False
        if op == RETURN_VALUE:
            self._generate_handler_edge(block, i, op, arg, WHY_RETURN)
        elif op == CONTINUE_LOOP:
            branched = self._generate_handler_edge(block, i, op, arg,
                                                   WHY_CONTINUE)
            assert branched, ("Attempted to continue outside of loop %r" %
                              (self.blocks[block][-1],))
        elif op == BREAK_LOOP:
            branched = self._generate_handler_edge(block, i, op, arg,
                                                   WHY_BREAK)
            assert branched, ("Attempted to break outside of loop %r" %
                              (self.blocks[block][-1],))
        elif op == END_FINALLY:
            # XXX Should we detect cases where return, continue, and
            # break appear inside the try-block?  This would create
            # more accurate control flow graphs by eliding edges we
            # know won't be taken.
            self._generate_handler_edge(block, i, op, arg, WHY_EXCEPTION)
            self._generate_handler_edge(block, i, op, arg, WHY_RETURN)
            self._generate_handler_edge(block, i, op, arg, WHY_BREAK)
            self._generate_handler_edge(block, i, op, arg, WHY_CONTINUE)
            goto_next = True # why == WHY_NOT
        elif op in opcode.hasjabs:
            self.cfg.add_edge(block, arg)
        elif op in opcode.hasjrel:
            self.cfg.add_edge(block, i + arg + 3)
        else:
            goto_next = True
        if op in opcode_util.hascbranch or goto_next:
            self.cfg.add_edge(block, self._get_next_block(block))

    def op_LOAD_FAST (self, i, op, arg, *args, **kws):
        self.cfg.blocks_reads[self.block].add(arg)
        return super(ControlFlowBuilder, self).op_LOAD_FAST(i, op, arg, *args,
                                                            **kws)

    def op_STORE_FAST (self, i, op, arg, *args, **kws):
        self.cfg.writes_local(self.block, i, arg)
        return super(ControlFlowBuilder, self).op_STORE_FAST(i, op, arg, *args,
                                                             **kws)

    def op_SETUP_EXCEPT (self, i, op, arg, *args, **kws):
        self.control_stack.append((i, op, arg))
        return super(ControlFlowBuilder, self).op_SETUP_EXCEPT(i, op, arg,
                                                               *args, **kws)

    def op_SETUP_FINALLY (self, i, op, arg, *args, **kws):
        self.control_stack.append((i, op, arg))
        return super(ControlFlowBuilder, self).op_SETUP_FINALLY(i, op, arg,
                                                                *args, **kws)

    def op_SETUP_LOOP (self, i, op, arg, *args, **kws):
        self.control_stack.append((i, op, arg))
        return super(ControlFlowBuilder, self).op_SETUP_LOOP(i, op, arg, *args,
                                                             **kws)

    def op_SETUP_WITH (self, i, op, arg, *args, **kws):
        self.control_stack.append((i, op, arg))
        return super(ControlFlowBuilder, self).op_SETUP_WITH(i, op, arg, *args,
                                                             **kws)

    def op_POP_BLOCK (self, i, op, arg, *args, **kws):
        self.control_stack.pop()
        return super(ControlFlowBuilder, self).op_POP_BLOCK(i, op, arg, *args,
                                                            **kws)

# ______________________________________________________________________

def build_cfg (func):
    '''Given a Python function, create a bytecode flow, visit the flow
    object, and return a control flow graph.'''
    co_obj = opcode_util.get_code_object(func)
    return ControlFlowBuilder().visit(opcode_util.build_basic_blocks(co_obj),
                                      co_obj.co_argcount)

# ______________________________________________________________________
# Main (self-test) routine

def main (*args, **kws):
    from tests import llfuncs
    if not args:
        args = ('doslice',)
    for arg in args:
        build_cfg(getattr(llfuncs, arg)).pprint()

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of byte_control.py
