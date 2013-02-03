import os.path, importlib

def _init():
    for fname in os.listdir(os.path.dirname(__file__)):
        if ((fname.endswith('.py') or fname.endswith('.pyc')) and
            not fname.startswith('__init__')):
            modname = os.path.basename(fname).rsplit('.', 1)[0]
            importlib.import_module('.' + modname, __name__)

_init()
