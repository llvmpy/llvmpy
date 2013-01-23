#include <Python.h>
#include <llvm/Support/Dwarf.h>

namespace llvmpy {
namespace dwarf {

using namespace llvm::dwarf;

const char *constant_names[] = {
    "LLVMDebugVersion",

    #define define(x) #x,
    #include "_dwarf.h"
    #undef define
};

int constant_values[] = {
    llvm::LLVMDebugVersion,

    #define define(x) x,
    #include "_dwarf.h"
    #undef define
};

enum enum_values {
    __llvmpy_LLVMDebugVersion,

    #define define(x) __llvmpy_##x,
    #include "_dwarf.h"
    #undef define

    NVALUES /* Get the number of constants */
};

} // End namespace dwarf

int
set_dwarf_constants(PyObject *module)
{
    int i;
    for (i = 0; i < dwarf::NVALUES; i++) {
        if (PyModule_AddIntConstant(module, dwarf::constant_names[i],
                                    dwarf::constant_values[i]) > 0)
            return -1;
    }

    return 0;
}

} // End namespace llvmpy

#if (PY_MAJOR_VERSION >= 3)
    struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_dwarf",
        NULL,
        -1,
        NULL, /* m_methods */
        NULL, /* m_reload */
        NULL, /* m_traverse */
        NULL, /* m_clear */
        NULL, /* m_free */
    };

    #define INITERROR return NULL
    PyObject *PyInit__dwarf(void)
#else
    #define INITERROR return
    PyMODINIT_FUNC init_dwarf(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create( &module_def );
#else
    PyObject *module = Py_InitModule("_dwarf", NULL);
#endif
    if (module == NULL)
        INITERROR;

    if (llvmpy::set_dwarf_constants(module) < 0)
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
