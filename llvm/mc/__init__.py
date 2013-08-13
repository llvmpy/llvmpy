from io import BytesIO
import contextlib

import llvm
from llvmpy import api

class Disassembler(llvm.Wrapper):

    @staticmethod
    def new(triple='', cpu='', features=''):
        if not triple:
            triple = api.llvm.sys.getDefaultTargetTriple()

        with contextlib.closing(BytesIO()) as error:
            target = api.llvm.TargetRegistry.lookupTarget(triple, error)
            if not target:
                raise llvm.LLVMException(error)
            if not target.hasMCDisassembler():
                raise llvm.LLVMException(target, "No disassembler provided for %s." % triple)

            sti = target.createMCSubtargetInfo(triple, cpu, features)
            if not sti:
                raise llvm.LLVMException("Could not create sub target info")

            return target.createMCDisassembler(sti)

