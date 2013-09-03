import sys

import llvm
if llvm.version < (3, 4):
    raise Exception("mc is not supported for llvm version less than 3.4")

from io import BytesIO
import contextlib

from llvmpy import api, extra
from llvmpy.api.llvm import MCDisassembler

class Operand(object):

    def __init__(self, mcoperand, target_machine):
        '''
        @mcoperand: an MCOperand object
        @target_machine: an llvm.target.TargetMachine object
        '''

        self.op = mcoperand
        if not self.op:
            raise llvm.LLVMException("null MCOperand argument")

        self.tm = target_machine

    def __str__(self):
        s = "invalid"
        if self.op.isReg():
            s = "reg(%s)" % (self.reg_name())
        elif self.op.isImm():
            s = "imm(0x%02x)" % (self.op.getImm())
        elif self.op.isFPImm():
            s = "imm(%r)" % (self.op.getFPImm())
        elif self.op.isExpr():
            s = "expr(%r)" % (self.op.getExpr().getKind())
        elif self.op.isInst():
            s = repr(Instr(self.op.getInst()))

        return s

    def __repr__(self):
        return str(self)

    def reg_name(self):
        if self.op.isReg():
            s = self.tm.reg_info.getName(self.op.getReg())
            if s.strip() == "":
                return "?"
            else:
                return s
        else:
            return ""

class Instr(object):

    def __init__(self, mcinst, target_machine):
        '''
        @mcinst: an MCInst object
        @target_machine: an llvm.target.TargetMachine object
        '''

        self.mcinst = mcinst
        if not self.mcinst:
            raise llvm.LLVMException("null MCInst argument")

        self.tm = target_machine

    def __str__(self):
        os = extra.make_raw_ostream_for_printing()
        self.tm.inst_printer.printInst(self.mcinst, os, "")
        return str(os.str())

    def __repr__(self):
        return str(self)

    def __len__(self):
        ''' the number of operands '''
        return int(self.mcinst.size())

    def operands(self):
        amt = self.mcinst.getNumOperands()
        if amt < 1:
            return []

        l = []
        for i in range(0, amt):
            l.append(Operand(self.mcinst.getOperand(i), self.tm))

        return l

    @property
    def instr_desc(self):
        return self.tm.instr_info.get(self.opcode)

    @property
    def flags(self):
        return self.instr_desc.getFlags()

    @property
    def ts_flags(self):
        return self.instr_desc.TSFlags

    @property
    def opcode(self):
        return self.mcinst.getOpcode()

    def is_branch(self):
        return self.tm.instr_analysis.isBranch(self.mcinst)

    def is_cond_branch(self):
        return self.tm.instr_analysis.isConditionalBranch(self.mcinst)

    def is_uncond_branch(self):
        return self.tm.instr_analysis.isUnconditionalBranch(self.mcinst)

    def is_indirect_branch(self):
        return self.tm.instr_analysis.isIndirectBranch(self.mcinst)

    def is_call(self):
        return self.tm.instr_analysis.isCall(self.mcinst)

    def is_return(self):
        return self.tm.instr_analysis.isReturn(self.mcinst)

    def is_terminator(self):
        return self.tm.instr_analysis.isTerminator(self.mcinst)

class BadInstr(Instr):
    pass

class Disassembler(object):

    def __init__(self, target_machine):
        self.tm = target_machine

    @property
    def mdasm(self):
        return self.tm.disassembler

    @property
    def mai(self):
        return self.tm.asm_info

    def instr(self, mcinst):
        return Instr(mcinst, self.tm)

    def bad_instr(self, mcinst):
        return BadInstr(mcinst, self.tm)

    def decode(self, bs, base_addr):
        '''
        decodes some the bytes in @bs into instructions and yields
        each instruction as it is decoded. @base_addr is the base address
        where the instruction bytes are from (not an offset into
        @bs). yields instructions in the form of (addr, data, inst) where
        addr is an integer, data is a tuple of integers and inst is an instance of
        llvm.mc.Instr
        '''

        if not isinstance(bs, bytes):
            if sys.version_info.major < 3:
                bs = bytes(bs)
            else:
                bs = bytes(map(lambda c: ord(c), bs))

        code = api.llvm.StringRefMemoryObject.new(bs, base_addr)
        idx = 0
        align = self.mai.getMinInstAlignment()

        while(idx < code.getExtent()):
            inst = api.llvm.MCInst.new()
            addr = code.getBase() + idx
            status, size = self.mdasm.getInstruction(inst, code, addr)

            if size < 1:
                size = (align - (idx % align))

            amt_left = code.getExtent() - idx
            if amt_left >= size:
                data = code.readBytes(addr, size)
            elif amt_left < 1:
                break 
            else:
                data = code.readBytes(addr, amt_left)

            if sys.version_info.major < 3:
                data = tuple(map(lambda b: ord(b), data))
            else:
                data = tuple(data)

            if status == MCDisassembler.DecodeStatus.Fail:
                yield (addr, data, None)
            elif status == MCDisassembler.DecodeStatus.SoftFail:
                yield (addr, data, self.bad_instr(inst))
            else:
                yield (addr, data, self.instr(inst))

            idx += size
