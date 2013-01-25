import sys
from binding import *
import codegen


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
    println()


def wrap_println_from_file(file):
    def println(s=''):
        file.write(s)
        file.write('\n')
    return println

def main():
    outputfilename = sys.argv[1]
    entry_modname = sys.argv[2]

    entry_module = __import__(entry_modname)

    units = []
    for ns in namespaces.values():
        print 'namespace', ns
        for fn in ns.functions:
            print fn
            units.append(fn)
        for cls in ns.classes:
            print cls
            units.append(cls)

    with open('%s.cpp' % outputfilename, 'w') as cppfile:
        println = wrap_println_from_file(cppfile)

        # extra headers
        populate_headers(println)

        # required headers
        includes = set()
        for u in units:
            includes |= u.includes

        for inc in includes:
            println('#include "%s"' % inc)
        println()

        # write methods and method tables
        for u in units:
            writer = codegen.CppCodeWriter(println)
            u.compile_cpp(writer)
        else:
            del writer

        # write function table
        writer = codegen.CppCodeWriter(println)
        writer.println('static')
        writer.println('PyMethodDef methtable[] = {')
        with writer.indent():
            fmt = '{ "%(name)s", (PyCFunction)%(func)s, METH_VARARGS, NULL },'
            for u in units:
                if isinstance(u, Function):
                    name = u.name
                    func = codegen.mangle(u.fullname)
                    writer.println(fmt % locals())
            writer.println('{ NULL },')
        writer.println('};')
        writer.println()
        del writer
        

        # write submodule table
        writer = codegen.CppCodeWriter(println)
        writer.println('static')
        writer.println('SubModuleEntry submodules[] = {')
        with writer.indent():
            for cls in units:
                if isinstance(cls, Class):
                    name = cls.name
                    table = codegen.mangle(cls.fullname)
                    writer.println('{ "%(name)s", %(table)s },' % locals())
            writer.println('{ "extra", extra_methodtable },')
            writer.println('{ NULL }')
        writer.println('};')
        writer.println('')
        del writer

        println(extension_entry % {'module': '_api', 'methtable': 'methtable'})

    with open('%s.py' % outputfilename, 'w') as pyfile:
        println = wrap_println_from_file(pyfile)
        println('import _api, capsule')
        println()
        for u in units:
            writer = codegen.PyCodeWriter(println)
            u.compile_py(writer)
        

if __name__ == '__main__':
    main()
