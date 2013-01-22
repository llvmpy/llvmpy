#include <Python.h>
#include <llvm_binding/capsule_context.h>

static
PyObject* getName(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)){
        return NULL;
    }
    const char* name = PyCapsule_GetName(obj);
    if (!name) return NULL;

    return PyString_FromString(name);
}

static
PyObject* getPointer(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)){
        return NULL;
    }
    void* pointer = PyCapsule_GetPointer(obj, PyCapsule_GetName(obj));
    if (!pointer) return NULL;

    return PyLong_FromVoidPtr(pointer);
}

static
PyObject* check(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)){
        return NULL;
    }
    if (PyCapsule_CheckExact(obj)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

// ------------------
// PyCapsule Context
// ------------------

static
CapsuleContext* getContext(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }
    void* context = PyCapsule_GetContext(obj);
    if (!context) {
        PyErr_SetString(PyExc_TypeError, "PyCapsule has no context.");
        return NULL;
    }
    return (CapsuleContext*)context;
}

static
PyObject* getClassName(PyObject* self, PyObject* args) {
    CapsuleContext* context = getContext(self, args);
    if (!context) {
        return NULL;
    } else {
        return PyString_FromString(context->className);
    }
}

static
PyObject* setDestructor(PyObject* self, PyObject* args) {
    PyObject* cap;
    PyObject* callable;
    if (!PyArg_ParseTuple(args, "OO", &cap, &callable)) {
        return NULL;
    }
    PyObject* arglist = Py_BuildValue("(O)", cap);
    CapsuleContext* context = getContext(self, arglist);
    Py_DECREF(arglist);
    if (!context) {
        return NULL;
    } else {
        void* ptr;
        if (callable != Py_None) {
            if (PyCallable_Check(callable)) {
                ptr = callable;
            } else {
                PyErr_SetString(PyExc_TypeError, "Argument is not callable.");
                return NULL;
            }
        } else {
            ptr = NULL;
        }
        context->destructor = (Destructor_Fn)ptr;
    }
    Py_RETURN_NONE;
}

static PyMethodDef core_methods[] = {
#define declmethod(func) { #func , ( PyCFunction )func , METH_VARARGS , NULL }
    declmethod(getName),
    declmethod(getPointer),
    declmethod(check),
    declmethod(getClassName),
    declmethod(setDestructor),
    { NULL },
#undef declmethod
};

// Module main function, hairy because of py3k port
extern "C" {

#if (PY_MAJOR_VERSION >= 3)
    struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_capsule",
        NULL,
        -1,
        core_methods,
        NULL, NULL, NULL, NULL
    };
#define INITERROR return NULL
    PyObject *
    PyInit__capsule(void)
#else
#define INITERROR return
    PyMODINIT_FUNC
    init_capsule(void)
#endif
    {
#if PY_MAJOR_VERSION >= 3
        PyObject *module = PyModule_Create( &module_def );
#else
        PyObject *module = Py_InitModule("_capsule", core_methods);
#endif
        if (module == NULL)
            INITERROR;
#if PY_MAJOR_VERSION >= 3
        
        return module;
#endif
    }
    
} // end extern C
