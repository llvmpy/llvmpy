#include "wrap.h"


/*===----------------------------------------------------------------------===*/
/* Type ctor/dtor                                                             */
/*===----------------------------------------------------------------------===*/

PyObject *ctor_LLVMModuleRef(LLVMModuleRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE; /* avoiding the `else' since we don't (want to) know what
                        the macro Py_RETURN_NONE expands to */
}

PyObject *ctor_LLVMTypeRef(LLVMTypeRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_LLVMValueRef(LLVMValueRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_LLVMTypeHandleRef(LLVMTypeHandleRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_LLVMBasicBlockRef(LLVMBasicBlockRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_LLVMBuilderRef(LLVMBuilderRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_LLVMModuleProviderRef(LLVMModuleProviderRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_LLVMMemoryBufferRef(LLVMMemoryBufferRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_LLVMPassManagerRef(LLVMPassManagerRef p)
{
    if (p)
        return PyCObject_FromVoidPtr(p, NULL);
    Py_RETURN_NONE;
}

PyObject *ctor_int(int i)
{
    return PyInt_FromLong(i);
}

_define_std_ctor(LLVMExecutionEngineRef)
_define_std_ctor(LLVMTargetDataRef)


/*===----------------------------------------------------------------------===*/
/* Helper functions                                                           */
/*===----------------------------------------------------------------------===*/

void *get_object_arg(PyObject *args)
{
    PyObject *o;

    if (!PyArg_ParseTuple(args, "O", &o))
        return NULL;
    
    return PyCObject_AsVoidPtr(o);
}

void **make_array_from_list(PyObject *list, int n)
{
    int i;
    void **arr;
    
    arr = (void **)malloc(sizeof(void *) * n);
    if (!arr)
        return NULL;

    for (i=0; i<n; i++) {
        PyObject *e = PyList_GetItem(list, i);
        arr[i] = PyCObject_AsVoidPtr(e);
    }
    
    return arr;
}
        
PyObject *make_list_from_LLVMTypeRef_array(LLVMTypeRef *p, unsigned n)
{
    int i;
    PyObject *list = PyList_New(n);

    if (!list)
        return NULL;

    for (i=0; i<n; i++) {
        PyObject *elem = ctor_LLVMTypeRef(p[i]);
        PyList_SetItem(list, i, elem);
    }

    return list;
}

