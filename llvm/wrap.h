/**
 * Functions and macros to aid in wrapping.
 */ 

#ifndef LLVM_PY_WRAP_H
#define LLVM_PY_WRAP_H


/* python includes */
#include <Python.h>
#include <structmember.h>

/* llvm includes */
#include "llvm-c/Core.h"
#include "llvm-c/Analysis.h"
#include "llvm-c/ExecutionEngine.h"
#include "llvm-c/Target.h"


/*===----------------------------------------------------------------------===*/
/* Type ctor/dtor                                                             */
/*===----------------------------------------------------------------------===*/

/* These are functions that can construct a PyCObject (a Python object that
 * holds an opaque pointer) from any time. The naming convention is significant,
 * this is assumed by the wrapper macros below. These are the equivalent of
 * what would in C++ have been specializations of a template function ctor<T>
 * for various types.
 */

#define _declare_std_ctor(typ)  \
PyObject * ctor_ ## typ ( typ p);

_declare_std_ctor(LLVMModuleRef)
_declare_std_ctor(LLVMTypeRef)
_declare_std_ctor(LLVMValueRef)
_declare_std_ctor(LLVMTypeHandleRef)
_declare_std_ctor(LLVMBasicBlockRef)
_declare_std_ctor(LLVMBuilderRef)
_declare_std_ctor(LLVMModuleProviderRef)
_declare_std_ctor(LLVMMemoryBufferRef)
_declare_std_ctor(LLVMPassManagerRef)
_declare_std_ctor(LLVMExecutionEngineRef)
_declare_std_ctor(LLVMTargetDataRef)
_declare_std_ctor(LLVMGenericValueRef)

/* standard types */
PyObject *ctor_int(int i);


/*===----------------------------------------------------------------------===*/
/* Helper methods                                                             */
/*===----------------------------------------------------------------------===*/

/**
 * Accept a single object argument of type PyCObject and return the
 * opaque pointer contained in it.
 */
void *get_object_arg(PyObject *args);

/**
 * Given a PyList object (list) having n (= PyList_Size(list)) elements,
 * each list object being a PyCObject, return a malloc()-ed array of
 * opaque pointers from the PyCObjects. The 'n' is passed explicitly
 * since the caller will have to query it once anyway, and we can avoid
 * a second call internally.
 */
void **make_array_from_list(PyObject *list, int n);

/**
 * Given an array of LLVMTypeRef's, create a PyList object. Note that
 * currently such an action is required only for LLVMTypeRef's, when
 * it is required another type, this method has to be generalized.
 */
PyObject *make_list_from_LLVMTypeRef_array(LLVMTypeRef *p, unsigned n);


/*===----------------------------------------------------------------------===*/
/* Wrapper macros                                                             */
/*===----------------------------------------------------------------------===*/

/* The following wrapper macros define functions that wrap over LLVM-C APIs
 * of various signatures. Though they look hairy, they all follow some
 * conventions.
 */

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1)
 */
#define _wrap_obj2obj(func, intype1, outtype)           \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    intype1 arg1;                                       \
                                                        \
    if (!(arg1 = ( intype1 )get_object_arg(args)))      \
        return NULL;                                    \
                                                        \
    return ctor_ ## outtype ( func (arg1));             \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(int arg1)
 */
#define _wrap_int2obj(func, outtype)                    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    int arg1;                                           \
                                                        \
    if (!PyArg_ParseTuple(args, "i", &arg1))            \
        return NULL;                                    \
                                                        \
    return ctor_ ## outtype ( func (arg1));             \
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2)
 */
#define _wrap_objobj2obj(func, intype1, intype2, outtype)   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2;                              \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2));       \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, intype2 arg2)
 */
#define _wrap_objobj2none(func, intype1, intype2)       \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2;                              \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
                                                        \
    func (arg1, arg2);                                  \
    Py_RETURN_NONE;                                     \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, <unsigned/signed int> arg2)
 */
#define _wrap_objint2obj(func, intype1, outtype)        \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1;                                     \
    intype1 arg1;                                       \
    unsigned int arg2;                                  \
                                                        \
    if (!PyArg_ParseTuple(args, "OI", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2));       \
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3)
 */
#define _wrap_objobjobj2obj(func, intype1, intype2, intype3, outtype)   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2, *obj3;                       \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    intype3 arg3;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3)); \
}

/**
 * Wrap LLVM functions of the type 
 * void func(intype1 arg1, intype2 arg2, intype3 arg3)
 */
#define _wrap_objobjobj2none(func, intype1, intype2, intype3)   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2, *obj3;                       \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    intype3 arg3;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
                                                        \
    func (arg1, arg2, arg3);                            \
    Py_RETURN_NONE;                                     \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(<unsigned/signed int> arg1, intype2 arg2, intype3 arg3)
 */
#define _wrap_intobjobj2obj(func, intype2, intype3, outtype)    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    unsigned int arg1;                                  \
    PyObject *obj2, *obj3;                              \
    intype2 arg2;                                       \
    intype3 arg3;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "IOO", &arg1, &obj2, &obj3))    \
        return NULL;                                    \
                                                        \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3)); \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(const char *s)
 */
#define _wrap_str2obj(func, outtype)                    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    const char *arg1;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "s", &arg1))            \
        return NULL;                                    \
                                                        \
    return ctor_ ## outtype ( func (arg1));             \
}

/**
 * Wrap LLVM functions of the type
 * outtype func()
 */
#define _wrap_none2obj(func, outtype)                   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    if (!PyArg_ParseTuple(args, ""))                    \
        return NULL;                                    \
                                                        \
    return ctor_ ## outtype ( func ());                 \
}

/**
 * Wrap LLVM functions of the type
 * const char *func(intype1 arg1)
 */
#define _wrap_obj2str(func, intype1)                    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    intype1 arg1;                                       \
                                                        \
    if (!(arg1 = ( intype1 )get_object_arg(args)))      \
        return NULL;                                    \
                                                        \
    return PyString_FromString( func (arg1));           \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1)
 */
#define _wrap_obj2none(func, intype1)                   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    intype1 arg1;                                       \
                                                        \
    if (!(arg1 = ( intype1 )get_object_arg(args)))      \
        return NULL;                                    \
                                                        \
    func (arg1);                                        \
    Py_RETURN_NONE;                                     \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, const char *arg2)
 */
#define _wrap_objstr2none(func, intype1)                \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1;                                     \
    const char *arg2;                                   \
    intype1 arg1;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "Os", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
                                                        \
    func (arg1, arg2);                                  \
    Py_RETURN_NONE;                                     \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, const char *arg2)
 */
#define _wrap_objstr2obj(func, intype1, outtype)        \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1;                                     \
    const char *arg2;                                   \
    intype1 arg1;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "Os", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2));       \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, <unsigned/signed int> arg2)
 */
#define _wrap_objint2none(func, intype1)                \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1;                                     \
    int arg2;                                           \
    intype1 arg1;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "Oi", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
                                                        \
    func (arg1, arg2);                                  \
    Py_RETURN_NONE;                                     \
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2, const char *arg3)
 */
#define _wrap_objobjstr2obj(func, intype1, intype2, outtype)    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2;                              \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    const char *arg3;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "OOs", &obj1, &obj2, &arg3))   \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3)) ;\
}

/**
 * Wrap LLVM functions of the type 
 * void func(intype1 arg1, <unsigned/signed int> arg2, <unsigned/signed int> arg3)
 */
#define _wrap_objintint2none(func, intype1)             \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1;                                     \
    intype1 arg1;                                       \
    int arg2, arg3;                                     \
                                                        \
    if (!PyArg_ParseTuple(args, "Oii", &obj1, &arg2, &arg3))  \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
                                                        \
    func (arg1, arg2, arg3);                            \
    Py_RETURN_NONE;                                     \
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, const char *arg2, intype3 arg3)
 */
#define _wrap_objstrobj2obj(func, intype1, intype3, outtype)    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj3;                              \
    intype1 arg1;                                       \
    const char *arg2;                                   \
    intype3 arg3;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "OsO", &obj1, &arg2, &obj3))   \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3)); \
}


/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2, int arg3, const char *arg4)
 */
#define _wrap_objobjintstr2obj(func, intype1, intype2, outtype)    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2;                              \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    int arg3;                                           \
    const char *arg4;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "OOis", &obj1, &obj2, &arg3, &arg4))   \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3, arg4)) ;\
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, const char *arg4)
 */
#define _wrap_objobjobjstr2obj(func, intype1, intype2, intype3, outtype)    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2, *obj3;                       \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    intype3 arg3;                                       \
    const char *arg4;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "OOOs", &obj1, &obj2, &obj3, &arg4))   \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3, arg4));   \
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, <unsigned/signed int> arg4)
 */
#define _wrap_objobjobjint2obj(func, intype1, intype2, intype3, outtype)    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2, *obj3;                       \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    intype3 arg3;                                       \
    int arg4;                                           \
                                                        \
    if (!PyArg_ParseTuple(args, "OOOi", &obj1, &obj2, &obj3, &arg4))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3, arg4));   \
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, intype arg4)
 */
#define _wrap_objobjobjobj2obj(func, intype1, intype2, intype3, intype4, outtype)   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2, *obj3, *obj4;                \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    intype3 arg3;                                       \
    intype4 arg4;                                       \
                                                        \
    if (!PyArg_ParseTuple(args, "OOOO", &obj1, &obj2, &obj3, &obj4))    \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
    arg4 = ( intype4 ) PyCObject_AsVoidPtr(obj4);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3, arg4));    \
}

/**
 * Wrap LLVM functions of the type 
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, intype arg4, const char *arg5)
 */
#define _wrap_objobjobjobjstr2obj(func, intype1, intype2, intype3, intype4, outtype)    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj2, *obj3, *obj4;                \
    intype1 arg1;                                       \
    intype2 arg2;                                       \
    intype3 arg3;                                       \
    intype4 arg4;                                       \
    const char *arg5;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "OOOOs", &obj1, &obj2, &obj3, &obj4, &arg5))   \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
    arg4 = ( intype4 ) PyCObject_AsVoidPtr(obj4);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3, arg4, arg5)); \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, int arg2, intype3 arg3, intype4 arg4, const char *arg5)
 */
#define _wrap_objintobjobjstr2obj(func, intype1, intype3, intype4, outtype) \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    PyObject *obj1, *obj3, *obj4;                       \
    intype1 arg1;                                       \
    int arg2;                                           \
    intype3 arg3;                                       \
    intype4 arg4;                                       \
    const char *arg5;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "OiOOs", &obj1, &arg2, &obj3, &obj4, &arg5))  \
        return NULL;                                    \
                                                        \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);       \
    arg3 = ( intype3 ) PyCObject_AsVoidPtr(obj3);       \
    arg4 = ( intype4 ) PyCObject_AsVoidPtr(obj4);       \
                                                        \
    return ctor_ ## outtype ( func (arg1, arg2, arg3, arg4, arg5)); \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 *arg2v, unsigned arg2n)
 * where arg2v is an array of intype2 elements, arg2n in length.
 */
#define _wrap_objlist2obj(func, intype1, intype2, outtype)      \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    PyObject *obj1, *obj2;                                      \
    intype1 arg1;                                               \
    intype2 *arg2v;                                             \
    unsigned arg2n;                                             \
    outtype ret;                                                \
                                                                \
    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))            \
        return NULL;                                            \
                                                                \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);               \
    arg2n = (unsigned) PyList_Size(obj2);                       \
    if (!(arg2v = ( intype2 *)make_array_from_list(obj2, arg2n)))   \
        return PyErr_NoMemory();                                \
                                                                \
    ret = func (arg1, arg2v, arg2n);                            \
    free(arg2v);                                                \
    return ctor_ ## outtype (ret);                              \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 *arg1v, unsigned arg1n, int arg2)
 * where arg1v is an array of intype1 elements, arg1n in length.
 */
#define _wrap_listint2obj(func, intype1, outtype)               \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    PyObject *obj1;                                             \
    int arg2;                                                   \
    intype1 *arg1v;                                             \
    unsigned arg1n;                                             \
    outtype ret;                                                \
                                                                \
    if (!PyArg_ParseTuple(args, "Oi", &obj1, &arg2))            \
        return NULL;                                            \
                                                                \
    arg1n = (unsigned) PyList_Size(obj1);                       \
    if (!(arg1v = ( intype1 *)make_array_from_list(obj1, arg1n))) \
        return PyErr_NoMemory();                                \
                                                                \
    ret = func (arg1v, arg1n, arg2);                            \
    free(arg1v);                                                \
    return ctor_ ## outtype (ret);                              \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 *arg1v, unsigned arg1n)
 * where arg1v is an array of intype1 elements, arg1n in length.
 */
#define _wrap_list2obj(func, intype1, outtype)                  \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    PyObject *obj1;                                             \
    intype1 *arg1v;                                             \
    unsigned arg1n;                                             \
    outtype ret;                                                \
                                                                \
    if (!PyArg_ParseTuple(args, "O", &obj1))                    \
        return NULL;                                            \
                                                                \
    arg1n = (unsigned) PyList_Size(obj1);                       \
    if (!(arg1v = ( intype1 *)make_array_from_list(obj1, arg1n))) \
        return PyErr_NoMemory();                                \
                                                                \
    ret = func (arg1v, arg1n);                                  \
    free(arg1v);                                                \
    return ctor_ ## outtype (ret);                              \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 *arg2v, unsigned arg2n, int arg3)
 * where arg2v is an array of intype2 elements, arg2n in length.
 */
#define _wrap_objlistint2obj(func, intype1, intype2, outtype)   \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    PyObject *obj1, *obj2;                                      \
    intype1 arg1;                                               \
    intype2 *arg2v;                                             \
    unsigned arg2n;                                             \
    int arg3;                                                   \
    outtype ret;                                                \
                                                                \
    if (!PyArg_ParseTuple(args, "OOi", &obj1, &obj2, &arg3))    \
        return NULL;                                            \
                                                                \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);               \
    arg2n = (unsigned) PyList_Size(obj2);                       \
    if (!(arg2v = ( intype2 *)make_array_from_list(obj2, arg2n)))   \
        return PyErr_NoMemory();                                \
                                                                \
    ret = func (arg1, arg2v, arg2n, arg3);                      \
    free(arg2v);                                                \
    return ctor_ ## outtype (ret);                              \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, int arg2, intype3 *arg3v, unsigned arg3n)
 * where arg3v is an array of intype3 elements, arg3n in length.
 */
#define _wrap_objintlist2obj(func, intype1, intype3, outtype)   \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    PyObject *obj1, *obj3;                                      \
    intype1 arg1;                                               \
    int arg2;                                                   \
    intype3 *arg3v;                                             \
    unsigned arg3n;                                             \
    outtype ret;                                                \
                                                                \
    if (!PyArg_ParseTuple(args, "OiO", &obj1, &arg2, &obj3))    \
        return NULL;                                            \
                                                                \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);               \
    arg3n = (unsigned) PyList_Size(obj3);                       \
    if (!(arg3v = ( intype3 *)make_array_from_list(obj3, arg3n)))   \
        return PyErr_NoMemory();                                \
                                                                \
    ret = func (arg1, arg2, arg3v, arg3n);                      \
    free(arg3v);                                                \
    return ctor_ ## outtype (ret);                              \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 *arg3v, unsigned arg3n)
 * where arg3v is an array of intype3 elements, arg3n in length.
 */
#define _wrap_objobjlist2obj(func, intype1, intype2, intype3, outtype)      \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    PyObject *obj1, *obj2, *obj3;                               \
    intype1 arg1;                                               \
    intype2 arg2;                                               \
    intype3 *arg3v;                                             \
    unsigned arg3n;                                             \
    outtype ret;                                                \
                                                                \
    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))    \
        return NULL;                                            \
                                                                \
    arg1 = ( intype1 ) PyCObject_AsVoidPtr(obj1);               \
    arg2 = ( intype2 ) PyCObject_AsVoidPtr(obj2);               \
    arg3n = (unsigned) PyList_Size(obj3);                       \
    if (!(arg3v = ( intype3 *)make_array_from_list(obj3, arg3n)))   \
        return PyErr_NoMemory();                                \
                                                                \
    ret = func (arg1, arg2, arg3v, arg3n);                      \
    free(arg3v);                                                \
    return ctor_ ## outtype (ret);                              \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 *arg3v, unsigned arg3n, const char *arg4)
 * where arg3v is an array of intype3 elements, arg3n in length.
 */
#define _wrap_objobjliststr2obj(func, intype1, intype2, intype3, outtype)   \
static PyObject *                                                   \
_w ## func (PyObject *self, PyObject *args)                         \
{                                                                   \
    PyObject *obj1, *obj2, *obj3;                                   \
    const char *arg4;                                               \
    intype1 arg1;                                                   \
    intype2 arg2;                                                   \
    intype3 *arg3v;                                                 \
    unsigned arg3n;                                                 \
    outtype ret;                                                    \
                                                                    \
    if (!PyArg_ParseTuple(args, "OOOs", &obj1, &obj2, &obj3, &arg4))\
        return NULL;                                                \
                                                                    \
    arg1  = ( intype1 ) PyCObject_AsVoidPtr(obj1);                  \
    arg2  = ( intype2 ) PyCObject_AsVoidPtr(obj2);                  \
    arg3n = ( unsigned ) PyList_Size(obj3);                         \
    if (!(arg3v = ( intype3 *)make_array_from_list(obj3, arg3n)))   \
        return PyErr_NoMemory();                                    \
                                                                    \
    ret = func (arg1, arg2, arg3v, arg3n, arg4);                    \
    free(arg3v);                                                    \
    return ctor_ ## outtype (ret);                                  \
}

/**
 * Wrap LLVM dump-to-string functions of the type
 * char *func(intype1)
 * where the return value has to be disposed after use by calling
 * LLVMDisposeMessage.
 */
#define _wrap_dumper(func, intype1)                                 \
static PyObject *                                                   \
_w ## func (PyObject *self, PyObject *args)                         \
{                                                                   \
    intype1 arg1;                                                   \
    char *val;                                                      \
    PyObject *ret;                                                  \
                                                                    \
    if (!(arg1= ( intype1 ) get_object_arg(args)))                  \
        return NULL;                                                \
                                                                    \
    val = func (arg1);                                              \
    ret = PyString_FromString(val);                                 \
    LLVMDisposeMessage(val);                                        \
    return ret;                                                     \
}

#endif /* LLVM_PY_WRAP_H */

