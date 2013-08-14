import llvm

from llvm import mc
from llvm.mc import Disassembler
from llvmpy import api

llvm.initialize_all_target_components()


def print_instructions(dasm, bs):
    for (offset, inst) in dasm.decode(bs):
        if inst is None:
            print("\t%r=>(bad): 0, []" % (offset))
        elif isinstance(inst, mc.BadInstr):
            print("\t%r=>(bad)%r: %r, %r" % (offset, inst, len(inst), inst.operands()))
        else:
            print("\t%r=>%r: %r, %r" % (offset, inst, len(inst), inst.operands()))


print("x86:")
print_instructions(Disassembler.x86(), "\x01\xc3\xc3\xcc\x90")
print("x86-64:")
print_instructions(Disassembler.x86_64(), "\x55\x48\x89\xe8")
#print("arm:")
#code = "\xe9\x2d\x40\x08\xe5\x9f\x00\x0c\xe5\x9f\x10\x0c" + \
#       "\xe5\x9f\x20\x0c\xe5\x9f\x30\x0c\xeb\xff\xff\xf6"
#print_instructions(Disassembler.arm(), code)

 


