from binding import *
from src.namespace import llvm
from src.Value import MDNode
from src.Instruction import Instruction, TerminatorInst
llvm.includes.add('llvm/Transforms/Utils/BasicBlockUtils.h')

SplitBlockAndInsertIfThen = llvm.Function('SplitBlockAndInsertIfThen',
                                          ptr(TerminatorInst),
                                          ptr(Instruction), # cmp
                                          cast(bool, Bool), # unreachable
                                          ptr(MDNode)) # branchweights

ReplaceInstWithInst = llvm.Function('ReplaceInstWithInst',
                                    Void,
                                    ptr(Instruction), # from
                                    ptr(Instruction)) # to
