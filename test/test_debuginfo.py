import os
import unittest

from llvm.core import *
from llvm import _dwarf, debuginfo

class TestDebugInfo(unittest.TestCase):

    def test_dwarf_constants(self):
        dwarf_constants = vars(_dwarf)

        # Version numbers
        self.assertIn("LLVMDebugVersion", dwarf_constants)
        self.assertIn("DWARF_VERSION", dwarf_constants)

        # Tags
        self.assertIn("DW_TAG_compile_unit", dwarf_constants)

        # Language identifiers
        self.assertIn("DW_LANG_Python", dwarf_constants)
        self.assertIn("DW_LANG_C89", dwarf_constants)
        self.assertIn("DW_LANG_C99", dwarf_constants)

        # print sorted([constname for constname in dwarf_constants
        #                             if constname.startswith("DW_LANG_")])

    def test_debug_info_compile_unit(self):
        mod = Module.new('test_debug_info')
        fty = Type.function(Type.float(), [Type.float()])
        square = mod.add_function(fty, 'square')
        bb = square.append_basic_block('entry')
        bldr = Builder.new(bb)

        source_filename = "test_debug_info.py"
        source_filedir = os.path.expanduser("~")

        # Debug info for our file
        filedesc = debuginfo.FileDescriptor(source_filename, source_filedir)

        # Debug info for our function
        subprogram = debuginfo.SubprogramDescriptor(
            filedesc,
            "some_function",
            "some_function",
            "some_function",
            filedesc,
            1,                          # line number
            debuginfo.empty,            # Type descriptor
            llvm_func=square,
        )
        subprograms = debuginfo.MDList([subprogram])

        # Debug info for our basic blocks
        blockdescr1 = debuginfo.BlockDescriptor(subprogram, 2, 4) # lineno, col
        blockdescr2 = debuginfo.BlockDescriptor(blockdescr1, 3, 4) # lineno, col

        # Debug info for our instructions
        posinfo1 = debuginfo.PositionInfoDescriptor(2, 4, blockdescr1)
        posinfo2 = debuginfo.PositionInfoDescriptor(2, 4, blockdescr2)

        # Debug info for our module
        compile_unit = debuginfo.CompileUnitDescriptor(
            # DW_LANG_Python segfaults:
            # llvm/ADT/StringRef.h:79: llvm::StringRef::StringRef(const char*):
            # Assertion `Str && "StringRef cannot be built from a NULL argument"'
            # _dwarf.DW_LANG_Python,
            _dwarf.DW_LANG_C89,
            source_filename,
            source_filedir,
            "my_cool_compiler",
            subprograms=subprograms,
        )

        # Define our module debug data
        compile_unit.define(mod)

        # Build some instructions
        value = square.args[0]
        result = bldr.fmul(value, value)
        ret = bldr.ret(result)

        # Annotate instructions with source position
        result.set_metadata("dbg", posinfo1.get_metadata(mod))
        ret.set_metadata("dbg", posinfo2.get_metadata(mod))

        # ... Aaaand, test...
        # print mod

        modstr = str(mod)

        # Test compile unit
        self.assertIn("my_cool_compiler", modstr)
        self.assertIn(source_filename, modstr)
        self.assertIn(source_filedir, modstr)
        self.assertIn("my_cool_compiler", modstr)

        # Test subprogram
        self.assertIn("some_function", modstr)
        self.assertIn("float (float)* @square", modstr)

if __name__ == '__main__':
#    TestDebugInfo("test_dwarf_constants").debug()
#    TestDebugInfo("test_debug_info_compile_unit").debug()
    unittest.main()