import os.path, importlib

def _init():
    base = os.path.dirname(__file__)
    for fname in os.listdir(base):
        print fname
        is_python_script = fname.endswith('.py') or fname.endswith('.pyc')
        is_init_script = fname.startswith('__init__')
        is_directory = os.path.isdir(os.path.join(base, fname))
        if (is_directory or is_python_script) and not is_init_script :
            modname = os.path.basename(fname).rsplit('.', 1)[0]
            importlib.import_module('.' + modname, __name__)

_init()

