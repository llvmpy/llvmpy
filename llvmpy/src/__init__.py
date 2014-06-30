from __future__ import print_function
import os.path
from binding import LLVM_VERSION

above_33 = ("MC")


last_mtime = 0

def _init(root=__name__, file=__file__):
    """
    This is reimported in everything subpackages and must be run in the
    __init__.py of them.
    """
    global last_mtime
    base = os.path.dirname(file)
    for fname in sorted(os.listdir(base)):
        is_python_script = fname.endswith('.py') or fname.endswith('.pyc')
        is_init_script = fname.startswith('__init__')
        is_directory = os.path.isdir(os.path.join(base, fname))
        is_python_module = is_directory and not fname.startswith('__')
        if (is_python_module or is_python_script) and not is_init_script:
            #print(fname)
            if fname in above_33 and LLVM_VERSION <= (3, 3):
                print("skip %s because llvm version is not above 3.3" % fname)
                continue

            modname = os.path.basename(fname).rsplit('.', 1)[0]
            #importlib.import_module('.' + modname, __name__)
            __import__('.'.join([root, modname]))

            mtime = os.path.getmtime(os.path.join(base, fname))
            last_mtime = max(last_mtime, mtime)

_init()

