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

        info = debuginfo.CompileUnitDescriptor(
            _dwarf.DW_LANG_Python,
            "test_debug_info.py",
            os.path.expanduser("~/"),
            "my_cool_compiler",
        )

        info.build_metadata(mod)

        value = square.args[0]
        result = bldr.fmul(value, value)
        bldr.ret(result)

#        info.build_metadata(mod)
        print mod
#        modstr = str(mod)
#        print modstr
        # self.assertIn("my_cool_compiler", modstr)

if __name__ == '__main__':
#    TestDebugInfo("test_dwarf_constants").debug()
    TestDebugInfo("test_debug_info_compile_unit").debug()
#    unittest.main()