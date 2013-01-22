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

        compile_unit = debuginfo.CompileUnitDescriptor(
            # DW_LANG_Python segfaults:
            # llvm/ADT/StringRef.h:79: llvm::StringRef::StringRef(const char*):
            # Assertion `Str && "StringRef cannot be built from a NULL argument"'
            # _dwarf.DW_LANG_Python,
            _dwarf.DW_LANG_C89,
            "test_debug_info.py",
            os.path.expanduser("~"),
            "my_cool_compiler",
        )

        filedesc = debuginfo.FileDescriptor.from_compileunit(compile_unit)

        subprogram = debuginfo.SubprogramDescriptor(
            compile_unit,
            "some_function",
            "some_function",
            "some_function",
            filedesc,
            1,                          # line number
            debuginfo.EmptyMetadata(),  # Type descriptor
            llvm_func=square,
        )
        subprograms = debuginfo.MDList([subprogram])

        # compile_unit.add_metadata("subprograms", subprograms)
        compile_unit.define(mod)
        subprogram.define(mod)

        value = square.args[0]
        result = bldr.fmul(value, value)
        bldr.ret(result)

        print mod

        modstr = str(mod)

        # Test compile unit
        self.assertIn("my_cool_compiler", modstr)
        self.assertIn("test_debug_info.py", modstr)
        self.assertIn(os.path.expanduser("~"), modstr)
        self.assertIn("my_cool_compiler", modstr)

        # Test subprogram
        self.assertIn("some_function", modstr)

if __name__ == '__main__':
#    TestDebugInfo("test_dwarf_constants").debug()
#    TestDebugInfo("test_debug_info_compile_unit").debug()
    unittest.main()