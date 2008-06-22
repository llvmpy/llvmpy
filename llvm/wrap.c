#include "wrap.h"


/*===----------------------------------------------------------------------===*/
/* Helper functions/macros                                                    */
/*===----------------------------------------------------------------------===*/

#define _define_std_ctor(typ)                   \
PyObject * ctor_ ## typ ( typ p)                \
{                                               \
    if (p)                                      \
        return PyCObject_FromVoidPtr(p, NULL);  \
    Py_RETURN_NONE;                             \
}


/*===----------------------------------------------------------------------===*/
/* Type ctor/dtor                                                             */
/*===----------------------------------------------------------------------===*/

_define_std_ctor(LLVMModuleRef)
_define_std_ctor(LLVMTypeRef)
_define_std_ctor(LLVMValueRef)
_define_std_ctor(LLVMTypeHandleRef)
_define_std_ctor(LLVMBasicBlockRef)
_define_std_ctor(LLVMBuilderRef)
_define_std_ctor(LLVMModuleProviderRef)
_define_std_ctor(LLVMMemoryBufferRef)
_define_std_ctor(LLVMPassManagerRef)
_define_std_ctor(LLVMExecutionEngineRef)
_define_std_ctor(LLVMTargetDataRef)
_define_std_ctor(LLVMGenericValueRef)

PyObject *ctor_int(int i)
{
    return PyInt_FromLong(i);
}


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

