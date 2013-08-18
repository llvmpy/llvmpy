import llvm
if llvm.version < (3, 4):
    raise Exception("mc is not supported for llvm version less than 3.4")

from io import BytesIO
import contextlib

from llvmpy import api
from llvmpy.api.llvm import MCDisassembler

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
            l.append(self.mcinst.getOperand(i))

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
        return Instr(mcinst, self)

    def bad_instr(self, mcinst):
        return BadInstr(mcinst, self)

    #decode some bytes into instructions. yields each instruction
    #as it is decoded.
    def decode(self, bs):
        code = api.llvm.StringRefMemoryObject.new(bs, 0)
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

