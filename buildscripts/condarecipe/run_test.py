import sys
import platform
import llvm
from llvm.ee import TargetMachine
target = TargetMachine.new()

print('target.triple=%r' % target.triple)
if sys.platform == 'darwin':
    s = {'64bit': 'x86_64', '32bit': 'x86'}[platform.architecture()[0]]
    assert target.triple.startswith(s + '-apple-darwin')

assert llvm.test(verbosity=2, run_isolated=False) == 0
print('llvm.__version__: %s' % llvm.__version__)
