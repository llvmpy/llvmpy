import os.path
from binding import LLVM_VERSION

above_33 = ("MC")

def _init(root=__name__, file=__file__):
    base = os.path.dirname(file)
    for fname in sorted(os.listdir(base)):
        is_python_script = fname.endswith('.py') or fname.endswith('.pyc')
        is_init_script = fname.startswith('__init__')
        is_directory = os.path.isdir(os.path.join(base, fname))
        is_python_module = is_directory and not fname.startswith('__')
        if (is_python_module or is_python_script) and not is_init_script:
            print(fname)
            if fname in above_33 and LLVM_VERSION <= (3, 3):
                print("skip %s because llvm version is not above 3.3" % fname)
                continue

            modname = os.path.basename(fname).rsplit('.', 1)[0]
            #importlib.import_module('.' + modname, __name__)
            __import__('.'.join([root, modname]))

_init()

