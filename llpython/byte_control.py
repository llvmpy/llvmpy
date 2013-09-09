# ______________________________________________________________________
from __future__ import absolute_import
import opcode
from . import opcode_util
import pprint

from .bytecode_visitor import BasicBlockVisitor, BenignBytecodeVisitorMixin
from .control_flow import ControlFlowGraph

# ______________________________________________________________________

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
        self.loop_stack = []
        for block in self.block_list:
            self.cfg.add_block(block, blocks[block])

    def exit_blocks (self, blocks):
        super(ControlFlowBuilder, self).exit_blocks(blocks)
        assert self.blocks == blocks
        self.cfg.compute_dataflow()
        self.cfg.update_for_ssa()
        ret_val = self.cfg
        del self.loop_stack
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

    def exit_block (self, block):
        assert block == self.block
        del self.block
        i, op, arg = self.blocks[block][-1]
        opname = opcode.opname[op]
        if op in opcode.hasjabs:
            self.cfg.add_edge(block, arg)
        elif op in opcode.hasjrel:
            self.cfg.add_edge(block, i + arg + 3)
        elif opname == 'BREAK_LOOP':
            loop_i, _, loop_arg = self.loop_stack[-1]
            self.cfg.add_edge(block, loop_i + loop_arg + 3)
        elif opname != 'RETURN_VALUE':
            self.cfg.add_edge(block, self._get_next_block(block))
        if op in opcode_util.hascbranch:
            self.cfg.add_edge(block, self._get_next_block(block))

    def op_LOAD_FAST (self, i, op, arg, *args, **kws):
        self.cfg.blocks_reads[self.block].add(arg)
        return super(ControlFlowBuilder, self).op_LOAD_FAST(i, op, arg, *args,
                                                            **kws)

    def op_STORE_FAST (self, i, op, arg, *args, **kws):
        self.cfg.writes_local(self.block, i, arg)
        return super(ControlFlowBuilder, self).op_STORE_FAST(i, op, arg, *args,
                                                             **kws)

    def op_SETUP_LOOP (self, i, op, arg, *args, **kws):
        self.loop_stack.append((i, op, arg))
        return super(ControlFlowBuilder, self).op_SETUP_LOOP(i, op, arg, *args,
                                                             **kws)

    def op_POP_BLOCK (self, i, op, arg, *args, **kws):
        self.loop_stack.pop()
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
