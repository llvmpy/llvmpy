#! /usr/bin/env python
# ______________________________________________________________________
# Module imports

from __future__ import absolute_import

from .byte_flow import BytecodeFlowBuilder

# ______________________________________________________________________
# Class definition(s)

class AddressFlowBuilder(BytecodeFlowBuilder):
    '''
    Builds on top of the BytecodeFlowBuilder with two important differences:

    * Child nodes are represented by bytecode indices.

    * All operations (other than purely stack manipulation operations)
      are retained in the block list (as opposed to being nested).

    The resulting data structure describes a directed acyclic graph
    (DAG) in a similar fashion to BytecodeFlowBuilder:

      * `flow_dag` ``:=`` ``{`` `blocks` ``*`` ``}``
      * `blocks` ``:=`` `block_index` ``:`` ``[`` `bytecode_tuple` ``*`` ``]``
      * `bytecode_tuple` ``:=`` ``(`` `opcode_index` ``,`` `opcode` ``,``
          `opname` ``,`` `arg` ``,`` ``[`` `opcode_index` ``*`` ``]`` ``)``
    '''
    def _visit_op(self, i, op, arg, opname, pops, pushes, appends):
        assert pops is not None, ('%s not well defined in opcode_util.'
                                  'OPCODE_MAP' % opname)
        if pops:
            if pops < 0:
                pops = arg - pops - 1
            assert pops <= len(self.stack), ("Stack underflow at instruction "
                                             "%d (%s)!" % (i, opname))
            stk_args = [stk_arg[0] for stk_arg in self.stack[-pops:]]
            del self.stack[-pops:]
        else:
            stk_args = []
        ret_val = (i, op, opname, arg, stk_args)
        if pushes:
            self.stack.append(ret_val)
        self.block.append(ret_val)
        return ret_val

    def op_IMPORT_FROM (self, i, op, arg):
        # References top of stack without popping, so we can't use the
        # generic machinery.
        opname = self.opmap[op][0]
        ret_val = i, op, opname, arg, [self.stack[-1][0]]
        self.stack.append(ret_val)
        self.block.append(ret_val)
        return ret_val

    def op_JUMP_IF_FALSE (self, i, op, arg):
        ret_val = i, op, self.opnames[op], arg, [self.stack[-1][0]]
        self.block.append(ret_val)
        return ret_val

    op_JUMP_IF_TRUE = op_JUMP_IF_FALSE

    def op_LIST_APPEND (self, i, op, arg):
        '''This method is used for both LIST_APPEND, and SET_ADD
        opcodes.'''
        elem = self.stack.pop()
        container = self.stack[-arg]
        ret_val = i, op, self.opnames[op], arg, [container[0], elem[0]]
        self.block.append(ret_val)
        return ret_val

    op_SET_ADD = op_LIST_APPEND

# ______________________________________________________________________
# Function definition(s)

def build_addr_flow(func):
    from . import byte_control
    cfg = byte_control.build_cfg(func)
    return AddressFlowBuilder().visit_cfg(cfg)

# ______________________________________________________________________
# Main (self-test) routine

def main(*args):
    import pprint
    from .tests import llfuncs
    if not args:
        args = ('pymod',)
    for arg in args:
        pprint.pprint(build_addr_flow(getattr(llfuncs, arg)))

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of addr_flow.py
