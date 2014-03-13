import sys
import platform
import llvm

from llvm.core import Module
from llvm.ee import EngineBuilder
from llvm.utils import check_intrinsics

m = Module.new('fjoidajfa')
eb = EngineBuilder.new(m)
target = eb.select_target()

print('target.triple=%r' % target.triple)
if sys.platform == 'darwin':
    s = {'64bit': 'x86_64', '32bit': 'x86'}[platform.architecture()[0]]
    assert target.triple.startswith(s + '-apple-darwin')

assert llvm.test(verbosity=2, run_isolated=False) == 0
check_intrinsics.main()

print('llvm.__version__: %s' % llvm.__version__)
#assert llvm.__version__ == '0.12.0'
