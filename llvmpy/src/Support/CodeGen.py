from binding import *
from ..namespace import llvm


Reloc = llvm.Namespace('Reloc')
Reloc.Enum('Model',
           'Default', 'Static', 'PIC_', 'DynamicNoPIC')

CodeModel = llvm.Namespace('CodeModel')
CodeModel.Enum('Model',
               'Default', 'JITDefault', 'Small', 'Kernel', 'Medium', 'Large')

TLSModel = llvm.Namespace('TLSModel')
TLSModel.Enum('Model',
             'GeneralDynamic', 'LocalDynamic', 'InitialExec', 'LocalExec')

CodeGenOpt = llvm.Namespace('CodeGenOpt')
CodeGenOpt.Enum('Level',
                'None', 'Less', 'Default', 'Aggressive')

