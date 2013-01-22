#include <Python.h>
#include <cstring>

#if (PY_MAJOR_VERSION >= 3)

static
PyObject*
create_python_module(const char *name, PyMethodDef* methtable){
    PyModuleDef module_def_tmp = {
        PyModuleDef_HEAD_INIT,
        name,
        NULL,
        -1,
        methtable,
        NULL, NULL, NULL, NULL
    };

    PyModuleDef* module_def = new PyModuleDef(module_def_tmp); // will leak??
    PyObject* module = PyModule_Create(module_def);
    if (module == NULL){
        delete module_def;
        return NULL;
    }
    return module;
}

#else

static
PyObject*
create_python_module(const char *name, PyMethodDef* methtable){
    PyObject* module = Py_InitModule(name, methtable);
    if (module == NULL) return NULL;
    return module;
}

#endif

static
PyObject*
create_python_submodule(PyObject* parent, const char* name,
                        PyMethodDef* methtable)
{
    const char* parentname = PyModule_GetName(parent);
    const unsigned len_parent = strlen(parentname);
    const unsigned len_sub = strlen(name);
    const unsigned len = len_parent + 1 + len_sub;
    char* fullname = new char[len + 1];
    strcpy(fullname, parentname);
    fullname[len_parent] = '.';
    strcpy(fullname + len_parent + 1, name);
    PyObject* submod = create_python_module(fullname, methtable);
    delete [] fullname;
    if (!submod)
        return NULL;
    if( -1 == PyModule_AddObject(parent, name, submod) )
        return NULL;
    return submod;
}

struct SubModuleEntry{
    const char* name;
    PyMethodDef* methtable;
};

static
int populate_submodules(PyObject* parent, SubModuleEntry* entries){
    for(SubModuleEntry* iter = entries; iter->name; ++iter){
        if (!create_python_submodule(parent, iter->name, iter->methtable))
            return 0;
    }
    return 1;
}