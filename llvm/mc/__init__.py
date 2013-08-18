import llvm
if llvm.version < (3, 4):
    raise Exception("mc is not supported for llvm version less than 3.4")

from io import BytesIO
import contextlib

from llvmpy import api
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

    def __repr__(self):
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

    def __repr__(self):
        return repr(self.mcinst)

    def __len__(self):
        return int(self.mcinst.size())

    def operands(self):
        amt = self.mcinst.getNumOperands()
        if amt < 1:
            return []

        l = []
        for i in range(0, amt):
            l.append(Operand(self.mcinst.getOperand(i), self.tm))

        return l

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

    def decode(self, bs, addr):
        '''
        decodes some the bytes in @bs into instructions and yields
        each instructionas it is decoded. @addr is the base address
        where the instruction bytes are from (not an offset into
        @bs)
        '''

        code = api.llvm.StringRefMemoryObject.new(bs, addr)
        idx = code.getBase()
        align = self.mai.getMinInstAlignment()

        while(idx < code.getExtent()):
            inst = api.llvm.MCInst.new()
            status, size = self.mdasm.getInstruction(inst, code, idx)

            if status == MCDisassembler.DecodeStatus.Fail:
                yield (idx, None)
            elif status == MCDisassembler.DecodeStatus.SoftFail:
                yield (idx, self.bad_instr(inst))
            else:
                yield (idx, self.instr(inst))

            if size < 1:
               idx += (align - (idx % align))
            else:
               idx += size

