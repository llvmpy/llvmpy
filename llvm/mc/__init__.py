import llvm
if llvm.version < (3, 4):
    raise Exception("mc is not supported for llvm version less than 3.4")

from io import BytesIO
import contextlib

from llvmpy import api
from llvmpy.api.llvm import MCDisassembler

class Instr:
    def __init__(self, mcinst):
        self.mcinst = mcinst
        if not self.mcinst:
            raise llvm.LLVMException("null MCInst argument")

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

class Disassembler:

    def __init__(self, mcdisasm, mri, mai, mii, mia, mip):
        self.mcdisasm = mcdisasm
        if not self.mcdisasm:
            raise llvm.LLVMException("null MCDisassembler argument")

        self.mri = mri
        self.mai = mai
        self.mii = mii
        self.mia = mia
        self.mip = mip

    def __repr__(self):
        return repr(self.mcdisasm)

    @staticmethod
    def new_from_target(target, triple, cpu, features):
        def raise_on_false(name, obj):
            if not obj:
                raise llvm.LLVMException("Could not create %s" % name)

        sti = target.createMCSubtargetInfo(triple, cpu, features)
        raise_on_false("subtarget info", sti)
        mri = target.createMCRegInfo(triple)
        raise_on_false("register info", mri)
        mai = target.createMCAsmInfo(mri, triple)
        raise_on_false("asm info", mai)
        mii = target.createMCInstrInfo()
        raise_on_false("instr info", mii)
        mia = target.createMCInstrAnalysis(mii)
        raise_on_false("instr analysis", mia)
        mip = target.createMCInstPrinter(mai.getAssemblerDialect(),
                                         mai, mii, mri, sti)

        return Disassembler(target.createMCDisassembler(sti),
                            mri, mai, mii, mia, mip)

    @staticmethod
    def new_from_triple(triple='', cpu='', features=''):
        if not triple:
            triple = api.llvm.sys.getDefaultTargetTriple()
            print repr(triple)

        with contextlib.closing(BytesIO()) as error:
            target = api.llvm.TargetRegistry.lookupTarget(triple, error)
            if not target:
                raise llvm.LLVMException(error.read())
            if not target.hasMCDisassembler():
                raise llvm.LLVMException(target, "No disassembler provided for %s." % triple)

        return Disassembler.new_from_target(target, triple, cpu, features)

    @staticmethod
    def new_from_name(name, cpu='', features=''):
        name = name.strip()
        for target in api.llvm.TargetRegistry.targetsList():
            if name == target.getName():
                return Disassembler.new_from_target(target, name, cpu, features)

        raise llvm.LLVMException("failed to find target with name %s" % name)
    
    @staticmethod
    def x86():
        return Disassembler.new_from_name('x86')

    @staticmethod
    def x86_64():
        return Disassembler.new_from_name('x86-64')

    @staticmethod
    def arm():
        return Disassembler.new_from_name('arm')

    @staticmethod
    def thumb():
        return Disassembler.new_from_name('thumb')

    #decode some bytes into instructions. yields each instruction
    #as it is decoded.
    def decode(self, bs):
        code = api.llvm.StringRefMemoryObject.new(bs, 0)
        idx = code.getBase()

        while(idx < code.getExtent()):
            inst = api.llvm.MCInst.new()
            status, size = self.mcdisasm.getInstruction(inst, code, idx)

            if status == MCDisassembler.DecodeStatus.Fail:
                yield (idx, None)
            elif status == MCDisassembler.DecodeStatus.SoftFail:
                yield (idx, BadInstr(inst))
            else:
                yield (idx, Instr(inst))

            if size <= 1:
               idx += 1
            else:
               idx += size

