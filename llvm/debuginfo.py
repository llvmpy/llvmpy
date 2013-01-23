"""
Support for debug info metadata.
"""

import functools

import llvm.core
from llvm import _dwarf

#----------------------------------------------------------------------------
# Some types and type checking functions
#----------------------------------------------------------------------------

int32_t = llvm.core.Type.int(32)
bool_t  = llvm.core.Type.int(1)
p_int32_t = llvm.core.Type.pointer(int32_t)
null = llvm.core.Constant.null(p_int32_t)

i32 = functools.partial(llvm.core.Constant.int, int32_t)
i1  = functools.partial(llvm.core.Constant.int, bool_t)

def is_md(value):
    return isinstance(value, (llvm.core.MetaData, llvm.core.NamedMetaData,
                              llvm.core.Value))

def is_mdstr(value):
    return isinstance(value, (llvm.core.MetaDataString, llvm.core.Value))

#----------------------------------------------------------------------------
# Callbacks for debug type descriptors
#----------------------------------------------------------------------------

def get_i32(llvm_module, value):
    return i32(value)

def get_i1(llvm_module, value):
    return i1(value)

def get_md(llvm_module, value):
    if is_md(value):
        return value
    return value.get_metadata(llvm_module)

def get_mdstr(llvm_module, value):
    if is_mdstr(value):
        return value
    return llvm.core.MetaDataString.get(llvm_module, value)

def get_mdlist(llvm_module, value):
    if isinstance(value, list):
        value = MDList([value])
    return get_md(llvm_module, value)

def get_lfunc(llvm_module, lfunc):
    assert lfunc.module is llvm_module
    return lfunc

#----------------------------------------------------------------------------
# Debug descriptors that generate LLVM Metadata
#----------------------------------------------------------------------------

class desc(object):
    """
    Descriptor of a debug field.

        field_name:
            name of the field (keyword argument name)
        build_metadata:
            metadata callback :: (llvm_module, Python value) -> LLVM Value
        default:
            default value for this field
    """

    def __init__(self, field_name, build_metadata, default=None):
        self.field_name = field_name
        self.build_metadata = build_metadata
        self.default = default


def build_operand_list(type_descriptors, idx2name, operands, kwargs):
    """
    Build the list of operands from the positional and keyword arguments
    to a DebugInfoDescriptor.

    E.g. FileDescriptor("foo.c", "/path/to/file", compile_unit=compile_unit)

        idx2name: {0 : 'source_filename',
                   1 : 'source_filedir',
                   2 : 'compile_unit' }
        operands: ["foo.c", "/path/to/file"]
        kwargs: { 'compile_unit' : compile_unit }
    """
    for i in range(len(operands), len(type_descriptors)):
        name = idx2name[i]
        if name in kwargs:
            op = kwargs[name]
        else:
            typedesc = type_descriptors[i]
            assert typedesc.default is not None, (
                        "No value found for field %s" % typedesc.field_name)
            op = typedesc.default

        operands.append(op)

    return operands


class DebugInfoDescriptor(object):
    """
    Base class to describe a debug info descriptor.

    See http://llvm.org/docs/SourceLevelDebugging.html
    """

    type_descriptors = None     # [desc(...)]
    idx2name = None             # { "field_idx" : field_name }
    name2idx = None             # { "field_name" : field_idx }

    # Whether the debug descriptor is allowed to be incomplete
    # The policy seems unclear ?
    accept_optional_data = False

    def __init__(self, *args, **kwargs):
        self.class_init()
        self.metadata_cache = {}

        operands = list(args)
        if kwargs or not self.accept_optional_data:
            operands = build_operand_list(self.type_descriptors,
                                          self.idx2name, operands, kwargs)

        self.operands = operands
        self.operands_dict = dict(
            (typedesc.field_name, operand)
                for typedesc, operand in zip(self.type_descriptors, operands))

    @classmethod
    def class_init(cls):
        if cls.idx2name is None and cls.type_descriptors is not None:
            cls.name2idx = {}
            cls.idx2name = {}

            for i, typedesc in enumerate(cls.type_descriptors):
                cls.name2idx[typedesc.field_name] = i
                cls.idx2name[i] = typedesc.field_name

    def add_metadata(self, metadata_name, metadata):
        """
        Replace a metadata value in the operand list.
        """
        idx = self.name2idx[metadata_name]
        self.operands[idx] = metadata

    #------------------------------------------------------------------------
    # Define metadata in a module
    #------------------------------------------------------------------------

    def get_metadata(self, llvm_module):
        """
        Get an existing metadata node for the given LLVM module, or build
        one from this instance.
        """
        if llvm_module in self.metadata_cache:
            node = self.metadata_cache[llvm_module]
        else:
            node = self.build_metadata(llvm_module)
            self.metadata_cache[llvm_module] = node

        return node

    def build_metadata(self, llvm_module):
        "Build a metadata node for the given LLVM module"
        mdops = []
        for type_desc, operand in zip(self.type_descriptors, self.operands):
            try:
                field_value = type_desc.build_metadata(llvm_module, operand)
            except Exception, e:
                if type_desc.build_metadata is get_md:
                    raise

                raise ValueError("Invalid value for field %r: %s" % (
                                                type_desc.field_name, e))

            mdops.append(field_value)

        return llvm.core.MetaData.get(llvm_module, mdops)

    def define(self, llvm_module):
        """
        Define this debug descriptor as named debug metadata for the module.
        """
        md = self.get_metadata(llvm_module)
        llvm.core.MetaData.add_named_operand(llvm_module, "dbg", md)

#----------------------------------------------------------------------------
# Convenience descriptors
#----------------------------------------------------------------------------

class MDList(DebugInfoDescriptor):
    """
    [MetaData]
    """

    def __init__(self, operands):
        self.type_descriptors = [desc("op", get_md)] * len(operands)
        super(MDList, self).__init__(*operands)

empty = MDList([])

#----------------------------------------------------------------------------
# Dwarf Debug descriptors
#----------------------------------------------------------------------------

class CompileUnitDescriptor(DebugInfoDescriptor):
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

    accept_optional_data = True

    type_descriptors = [
        desc("tag", get_i32),
        desc("unused", get_i32),

        # Positional argument list starts here:
        desc("langid", get_i32),
        desc("source_filename", get_mdstr),
        desc("source_filedir", get_mdstr),
        desc("producer", get_mdstr),
        desc("is_main", get_i1, default=False),
        desc("is_optimized", get_i1, default=False),
        desc("compile_flags", get_mdstr, default=""),
        desc("runtime_version", get_i32, default=0),
        desc("enum_types", get_mdlist, default=empty),
        desc("retained_types", get_mdlist, default=empty),
        desc("subprograms", get_mdlist, default=empty),
        desc("global_vars", get_mdlist, default=empty),
    ]

    def __init__(self, *args, **kwargs):
        super(CompileUnitDescriptor, self).__init__(
            _dwarf.DW_TAG_compile_unit + _dwarf.LLVMDebugVersion, # tag
            0,                                                    # unused
            *args, **kwargs)

    def define(self, llvm_module):
        """
        Define this debug descriptor as named debug metadata for the module.
        """
        md = self.get_metadata(llvm_module)
        llvm.core.MetaData.add_named_operand(llvm_module, "llvm.dbg.cu", md)


class FileDescriptor(DebugInfoDescriptor):
    """
    !0 = metadata !{
      i32,       ;; Tag = 41 + LLVMDebugVersion (DW_TAG_file_type)
      metadata,  ;; Source file name
      metadata,  ;; Source file directory (includes trailing slash)
      metadata   ;; Unused
    }
    """

    type_descriptors = [
        desc("tag", get_i32),

        # Positional argument list starts here:
        desc("source_filename", get_mdstr),
        desc("source_filedir", get_mdstr),
        desc("compile_unit", get_md, default=null),
    ]

    def __init__(self, *args, **kwargs):
        super(FileDescriptor, self).__init__(
            _dwarf.DW_TAG_file_type + _dwarf.LLVMDebugVersion, # Tag
            *args, **kwargs)

    @classmethod
    def from_compileunit(cls, compile_unit_descriptor):
        return cls(compile_unit_descriptor.operands_dict["source_filename"],
                   compile_unit_descriptor.operands_dict["source_filedir"],
                   compile_unit_descriptor)


class SubprogramDescriptor(DebugInfoDescriptor):
    """
    !2 = metadata !{
      i32,      ;; Tag = 46 + LLVMDebugVersion (DW_TAG_subprogram)
      i32,      ;; Unused field.
      metadata, ;; Reference to context descriptor
      metadata, ;; Name
      metadata, ;; Display name (fully qualified C++ name)
      metadata, ;; MIPS linkage name (for C++)
      metadata, ;; Reference to file where defined
      i32,      ;; Line number where defined
      metadata, ;; Reference to type descriptor
      i1,       ;; True if the global is local to compile unit (static)
      i1,       ;; True if the global is defined in the compile unit (not extern)
      i32,      ;; Line number where the scope of the subprogram begins
      i32,      ;; Virtuality, e.g. dwarf::DW_VIRTUALITY__virtual
      i32,      ;; Index into a virtual function
      metadata, ;; indicates which base type contains the vtable pointer for the
                ;; derived class
      i32,      ;; Flags - Artifical, Private, Protected, Explicit, Prototyped.
      i1,       ;; isOptimized
      Function * , ;; Pointer to LLVM function
      metadata, ;; Lists function template parameters
      metadata, ;; Function declaration descriptor
      metadata  ;; List of function variables
    }
    """

    accept_optional_data = True

    type_descriptors = [
        desc("tag", get_i32),
        desc("unused", get_i32),

        # Positional argument list starts here:
        desc("file_desc", get_md),
        desc("name", get_mdstr),
        desc("display_name", get_mdstr),
        desc("mips_linkage_name", get_mdstr),
        desc("source_file_ref", get_md),
        desc("line_number", get_i32),
        desc("signature", get_md),
        desc("is_local", get_i1, default=False),
        desc("is_definition", get_i1, default=True),
        desc("virtual_attribute", get_i32, default=0),
        desc("virtual_index", get_i32, default=0),
        desc("virttab", get_i32, default=0),
        desc("flags", get_i32, default=0),
        desc("is_optimized", get_i1, default=False),
        desc("llvm_func", get_lfunc),
        # Template params
        # Func decl
        # Func vars
    ]

    def __init__(self, *args, **kwargs):
        super(SubprogramDescriptor, self).__init__(
            _dwarf.DW_TAG_subprogram + _dwarf.LLVMDebugVersion, # Tag
            0,                                                  # Unused
            *args, **kwargs)

class BlockDescriptor(DebugInfoDescriptor):
    """
    !3 = metadata !{
      i32,     ;; Tag = 11 + LLVMDebugVersion (DW_TAG_lexical_block)
      metadata,;; Reference to context descriptor
      i32,     ;; Line number
      i32      ;; Column number
    }
    """

    type_descriptors = [
        desc("tag", get_i32),

        # Positional argument list starts here:
        desc("context_descr", get_md), # FileDescr | BlockDescr |
                                       # SubprogDescr | ComputeUnit
        desc("line_number", get_i32),
        desc("col_number", get_i32),
    ]

    def __init__(self, *args, **kwargs):
        super(BlockDescriptor, self).__init__(
            _dwarf.DW_TAG_lexical_block + _dwarf.LLVMDebugVersion,
            *args, **kwargs)

class PositionInfoDescriptor(DebugInfoDescriptor):
    """
    line number, column number, scope, and original scope
    """

    type_descriptors = [
        desc("line_number", get_i32),
        desc("col_number", get_i32),
        desc("context_descr", get_md),          # Scope of instruction
                                                # (FileDescr etc)
        desc("original_context_descr", get_md,  # The original scope if inlined
             default=null),
    ]
