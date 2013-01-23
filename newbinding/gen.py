import sys, logging
from binding import *
from utils import *
from cStringIO import StringIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

extension_entry = '''
    
extern "C" {

#if (PY_MAJOR_VERSION >= 3)
    
PyObject *
PyInit_%(module)s(void)
{
    PyObject *module = create_python_module("%(module)s", %(methtable)s);
    if (module) {
        if (populate_submodules(module, submodules))
            return module;
    }
    return NULL;
}

#else

PyMODINIT_FUNC
init%(module)s(void)
{
    PyObject *module = create_python_module("%(module)s", %(methtable)s);
    if (module) {
        populate_submodules(module, submodules);
    }
}
#endif

} // end extern C

'''

def build_methoddef(name, defns, println):
    println('static PyMethodDef %s[] = {' % name)
    for name, func in defns:
        println('{ "%(name)s", (PyCFunction)%(func)s, METH_VARARGS, NULL },' %
                locals())
    else:
        println('{ NULL }')
        println('};')
        println('')


class Context(object):
    def __init__(self):
        self.includes = set()
        self.functions = {}
        self.classes = {}
        self.definitions = []

    def generate_cpp(self, println):
        for i in self.includes:
            println('#include "%s"' % i)

        println('\n'.join(self.definitions))

        # global function
        defns = []
        for name, func in self.functions.items():
            defns.append((name, func.name))
        build_methoddef('global_functions', defns, println)

        # classes
        for name, cls in self.classes.items():
            defns = []
            for meth in cls.methods:
                defns.append((meth.name, meth.mangled_name))
            println("// %s" % cls.fullname)
            build_methoddef(cls.mangled_name, defns, println)

        println('static SubModuleEntry submodules[] = {')
        for name, cls in self.classes.items():
            table = cls.mangled_name
            println('{ "%(name)s", %(table)s },' % locals())
        println('{ "extra", extra_methodtable },')
        println('{ NULL }')
        println('};')
        println('')

        # generate entry
        println(extension_entry % {'module': '_api',
                                   'methtable': 'global_functions',})

    def generate_py(self, println):
        println('import _api, capsule')
        println('')
        # wraps all extras
        extra_wrapper = '''
def _init_extra_wrapper():
    def wrap(callee):
        def _wrapped(*args):
            args = map(capsule.unwrap, args)
            ret = callee(*args)
            return capsule.wrap(ret)
        return _wrapped
    for k in dir(_api.extra):
        v = getattr(_api.extra, k)
        if not k.startswith('__') and callable(v):
            globals()[k] = wrap(v)
_init_extra_wrapper()
        '''
        println(extra_wrapper)
        println('')
        # global function
        for name in self.functions:
            println('def %(name)s(*args):' % locals())
            println2 = indent_println(println)
            println2('args = map(capsule.unwrap, args)')
            println2('ptr = _api.%(name)s(*args)' % locals())
            println2('return capsule.wrap(ptr)')
            println('')
        # classes
        classes = sorted(self.classes.items(), key=lambda x: x[1].rank)

        for name, cls in classes:
            if isinstance(cls, Subclass):
                parent = cls.parent.name
            else:
                parent = 'capsule.Wrapper'
            println('@capsule.register_class')
            println('class %(name)s(%(parent)s):' % locals())
            self.generate_py_class(indent_println(println), cls)
            println('')

    def generate_py_class(self, println, cls):
        if len(cls.methods) == 0:
            println('pass')
        else:
            mod = cls.name
            # generate class enums
            for enum in cls.enums:
                println('class %s:' % enum.name)
                println2 = indent_println(println)
                for v in enum.values:
                    println2('%(v)s = "%(v)s"' % locals())
                println('')
            # generate class methods
            for method in cls.methods:
                name = method.name
                if(isinstance(method, StaticMethod) or
                   isinstance(method, StaticMultiMethod)):
                    println('@staticmethod')
                    println('def %(name)s(*args):' % locals())
                    println2 = indent_println(println)
                    println2('args = map(capsule.unwrap, args)')
                    println2('ret = _api.%(mod)s.%(name)s(*args)' % locals())
                    println2('return capsule.wrap(ret)')
                elif isinstance(method, Destructor):
                    println('_delete_ = _api.%(mod)s.%(name)s' % locals())
                else:
                    println('def %(name)s(self, *args):' % locals())
                    println2 = indent_println(println)
                    println2('args = map(capsule.unwrap, args)')
                    println2('ret = _api.%(mod)s.%(name)s(self._ptr, *args)' %
                             locals())
                    println2('return capsule.wrap(ret)')
                println('')

    def add_module(self, module):
        allsyms = [(k, v) for k, v in vars(module).items()
                   if isinstance(v, Binding)]
        symtab = sorted(allsyms, key=lambda x: x[1].rank)

        # generate includes
        for k, v in symtab:
            self.includes |= v.include

        # compile everything
        for k, v in symtab:
            buf = StringIO()
            def println_to_def(s):
                buf.write(s)
                buf.write('\n')
            logger.info('compiling %s', k)
            v.compile(k, println_to_def)
            self.definitions.append(buf.getvalue())
            buf.close()

        # generate py defintion table for global functions
        for k, v in symtab:
            if isinstance(v, Function):
                if v.name in self.functions:
                    raise NameError("Duplicated function name: %s" % v.name)
                self.functions[v.name] = v

        # generate sub module tables for classes
        submodules = []
        for k, v in symtab:
            if isinstance(v, Class):
                if v.name in self.classes:
                    if v is not self.classes[v.name]:
                        raise NameError("Duplicated class: %s" % v.name)
                self.classes[v.name] = v


def populate_headers(println):
    includes = [
                'llvm_binding/conversion.h',
                'llvm_binding/binding.h',
                'llvm_binding/llvm_extra.h',
                'llvm_binding/capsule_context.h',
                'llvm_binding/extra.h',             # extra submodule to add
                ]
    for inc in includes:
        println('#include "%s"' % inc)

def wrap_println(f):
    def println(s):
        f.write(s)
        f.write('\n')
    return println

if __name__ == '__main__':
    outputfilename = sys.argv[1]
    srcdir = sys.argv[2]
    modnames = sys.argv[3:]

    modules = []
    for m in modnames:
        path = '%s.%s' % (srcdir, m)
        logger.info("import module %s", path)
        module = __import__(path)
        for token in path.split('.')[1:]:
            module = getattr(module, token)
        modules.append(module)

    context = Context()

    for mod in modules:
        context.add_module(mod)

    with open('%s.cpp' % outputfilename, 'w') as outfile:
        println = wrap_println(outfile)
        populate_headers(println)
        context.generate_cpp(println)
    with open('%s.py' % outputfilename, 'w') as outfile:
        println = wrap_println(outfile)
        context.generate_py(println)

