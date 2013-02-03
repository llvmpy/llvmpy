from binding import *
from ..namespace import llvm

@llvm.Class()
class Reloc:
    Model = Enum('Default', 'Static', 'PIC_', 'DynamicNoPIC')

@llvm.Class()
class CodeModel:
    Model = Enum('Default', 'JITDefault', 'Small', 'Kernel', 'Medium', 'Large')

@llvm.Class()
class TLSModel:
    Model = Enum('GeneralDynamic', 'LocalDynamic', 'InitialExec', 'LocalExec')

@llvm.Class()
class CodeGenOpt:
    'Actually a namespace'
    Level = Enum('None', 'Less', 'Default', 'Aggressive')

