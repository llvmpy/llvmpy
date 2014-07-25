from __future__ import print_function
import sys, os, time
from binding import namespaces
import codegen


extension_entry = '''

extern "C" {

#if (PY_MAJOR_VERSION >= 3)

PyMODINIT_FUNC
PyInit_%(module)s(void)
{
PyObject *module = create_python_module("%(module)s", meth_%(ns)s);
if (module) {
if (populate_submodules(module, submodule_%(ns)s))
return module;
}
return NULL;
}

#else

PyMODINIT_FUNC
init%(module)s(void)
{
PyObject *module = create_python_module("%(module)s", meth_%(ns)s);
if (module) {
populate_submodules(module, submodule_%(ns)s);
}
}
#endif

} // end extern C

'''


def populate_headers(println):
    includes = [
        'cstring',
        'Python.h',
        'python3adapt.h',
        'capsulethunk.h',
        'llvm_binding/conversion.h',
        'llvm_binding/binding.h',
        'llvm_binding/capsule_context.h',
        'llvm_binding/extra.h', # extra submodule to add
    ]
    for inc in includes:
        println('#include "%s"' % inc)
    println()


FILE_HEADER = """// This file is generated automatically
// Python: 0x%x
""" % (sys.hexversion,)


def main():
    print("Running LLVM API generator")
    outputfilename = sys.argv[1]
    entry_modname = sys.argv[2]
    sys.path += [os.path.dirname(os.curdir)]
    entry_module = __import__(entry_modname)
    rootns = namespaces['']

    # Check if files are modified

    outputfilepath = '%s.cpp' % outputfilename
    try:
        mtime = os.path.getmtime(outputfilepath)
    except OSError:
        mtime = 0

    if entry_module.last_mtime <= mtime:

        # Check if file header matches
        with open(outputfilepath) as checkfile:
            n = len(FILE_HEADER)
            header = checkfile.read(n)

        if header == FILE_HEADER:
            print("up to date")
            return
        else:
            print("file is outdated")
            pass

    # Generate C++ source
    with open(outputfilepath, 'w') as cppfile:
        println = codegen.wrap_println_from_file(cppfile)
        println(FILE_HEADER)
        populate_headers(println)                  # extra headers
        # print all includes
        for inc in rootns.aggregate_includes():
            println('#include "%s"' % inc)
        println()
        # print all downcast
        downcast_fns = rootns.aggregate_downcast()
        for ((fromty, toty), fn) in downcast_fns:
            name = fn.name
            fmt = '''
static
%(toty)s* %(name)s(%(fromty)s* arg)
{
    return typecast< %(toty)s >::from(arg);
}
'''
            println(fmt % locals())

            fn.generate_cpp(println)

        println('static')
        println('PyMethodDef downcast_methodtable[] = {')
        fmt = '{ "%(name)s", (PyCFunction)%(func)s, METH_VARARGS, NULL },'
        for _, fn in downcast_fns:
            name = fn.name
            func = fn.c_name
            println(fmt % locals())
        println('{ NULL }')
        println('};')
        println()
        # generate submodule
        rootns.generate_cpp(println, extras=[('extra', 'extra_methodtable'),
                                             ('downcast',
                                              'downcast_methodtable')])
        println(extension_entry % {'module': '_api',
                                   'ns': ''})

    # Generate Python source
    rootns.generate_py(rootdir='.', name='api')


if __name__ == '__main__':
    main()
