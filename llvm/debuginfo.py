"""
Support for debug info metadata.
"""

import functools

import llvm.core
from llvm import _dwarf

int32_t = llvm.core.Type.int(32)
bool_t  = llvm.core.Type.int(1)

i32 = functools.partial(llvm.core.Constant.int, int32_t)
i1  = functools.partial(llvm.core.Constant.int, bool_t)

class CompileUnitDescriptor(object):
    """
    !0 = metadata !{
      i32,       ;; Tag = 17 + LLVMDebugVersion (DW_TAG_compile_unit)
      i32,       ;; Unused field.
      i32,       ;; DWARF language identifier (ex. DW_LANG_C89)
      metadata,  ;; Source file name
      metadata,  ;; Source file directory (includes trailing slash)
      metadata   ;; Producer (ex. "4.0.1 LLVM (LLVM research group)")
      i1,        ;; True if this is a main compile unit.
      i1,        ;; True if this is optimized.
      metadata,  ;; Flags
      i32        ;; Runtime version
      metadata   ;; List of enums types
      metadata   ;; List of retained types
      metadata   ;; List of subprograms
      metadata   ;; List of global variables
    }
    """

    def __init__(self, langid, source_filename, source_filedir,
                 producer, is_main=False, is_optimized=False,
                 compile_flags=None, runtime_version=0, enum_types=None,
                 retained_types=None, subprograms=None, global_vars=None):
        self.langid = langid
        self.source_filename = source_filename
        self.source_filedir = source_filedir
        self.producer = producer
        self.is_main = is_main
        self.is_optimized = is_optimized
        self.compile_flags = compile_flags
        self.runtime_version = runtime_version
        self.enum_types = enum_types
        self.retained_types = retained_types
        self.subprograms = subprograms
        self.global_vars = global_vars

    def build_metadata(self, llvm_module):
        md = functools.partial(llvm.core.MetaData.get, llvm_module)
        mstr = functools.partial(llvm.core.MetaDataString.get, llvm_module)

        operands = [
            i32(_dwarf.DW_TAG_compile_unit +
                _dwarf.LLVMDebugVersion),       # tag
            i32(0),                             # unused
            i32(self.langid),                   # Language identifier
            mstr(self.source_filename),
            mstr(self.source_filedir),
            mstr(self.producer),
            i1(self.is_main),
            i1(self.is_optimized),
            mstr(self.compile_flags or ""),
            md(self.enum_types or []),
            md(self.retained_types or []),
            md(self.subprograms or []),
            md(self.global_vars or []),
        ]

#        for op in operands:
#            print op

        node = llvm.core.MetaData.get(llvm_module, operands)
        llvm.core.MetaData.add_named_operand(llvm_module, "dbg", node)

#        print "printing metadata compile unit..."
#        print node
#        print "---- done ----"

        return node
