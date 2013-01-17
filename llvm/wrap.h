/*
 * Copyright (c) 2008-10, Mahadevan R All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *  * Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 *  * Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 *  * Neither the name of this software, nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * Functions and macros to aid in wrapping.
 */

#ifndef LLVM_PY_WRAP_H
#define LLVM_PY_WRAP_H


/* python includes */
#include <Python.h>
//  #include <structmember.h> //unused?

//// For pre-2.7 compatbility, use the following include, which provides
//// alias for PyCapsule.
//// See http://docs.python.org/py3k/howto/cporting.html
#include "capsulethunk.h"   // pre-2.7 compatibility for PyCapsule


/* llvm includes */
#include "llvm-c/Core.h"
#include "llvm-c/Analysis.h"
#include "llvm-c/ExecutionEngine.h"
#include "llvm-c/Target.h"

// workaround missing bool type
#define bool int
#include "llvm-c/Transforms/PassManagerBuilder.h"
#undef bool

#include "llvm_c_extra.h"

#include <new>
#include <sstream>

class py_exception: public std::exception{};

#define LLVMPY_TRY                                \
    try {

#define LLVMPY_CATCH_ALL                                 \
    } catch (const std::bad_alloc&) {                    \
        return PyErr_NoMemory();                         \
    } catch (const py_exception &) {                     \
        return NULL;                                     \
    } catch (const std::exception& e) {                  \
        PyErr_SetString(PyExc_RuntimeError, e.what());   \
        return NULL;                                     \
    } catch (...) {                                      \
        std::ostringstream oss;                                         \
        oss << "Unknown exception " << __FILE__ << ":" << __LINE__;     \
        PyErr_SetString(PyExc_RuntimeError, oss.str().c_str());         \
        return NULL;                                                    \
    }

/*===----------------------------------------------------------------------===*/
/* Typedefs                                                                   */
/*===----------------------------------------------------------------------===*/

typedef unsigned long long llvmwrap_ull;
typedef long long llvmwrap_ll;

/*===----------------------------------------------------------------------===*/
/* Type ctor/dtor                                                             */
/*===----------------------------------------------------------------------===*/

extern const char PYCAP_OBJECT_NAME[] ;

// Cast python object to aTYPE
template <typename aTYPE>
aTYPE pycap_get( PyObject* obj )
{
    void *p = PyCapsule_GetPointer(obj, PYCAP_OBJECT_NAME);
    if (!p){
        throw py_exception();
    }
    return static_cast<aTYPE> (p);
}

// Contruct python object to hold aTYPE pointer
template <typename aTYPE>
PyObject* pycap_new( aTYPE p )
{
    if (p){
        return PyCapsule_New(p, PYCAP_OBJECT_NAME, NULL);
    }
    Py_RETURN_NONE;
}

/*===----------------------------------------------------------------------===*/
/* Helper methods                                                             */
/*===----------------------------------------------------------------------===*/

/**
 * Accept a single object argument of type PyCObject and return the
 * opaque pointer contained in it.
 */
void *get_object_arg(PyObject *args);

template <typename aTYPE>
aTYPE get_object_arg( PyObject* obj )
{
    return static_cast<aTYPE> ( get_object_arg(obj) );
}

/**
 * Given a PyList object (list) having n (= PyList_Size(list)) elements,
 * each list object being a PyCObject, return a new()-ed array of
 * opaque pointers from the PyCObjects. The 'n' is passed explicitly
 * since the caller will have to query it once anyway, and we can avoid
 * a second call internally.
 */
void **make_array_from_list(PyObject *list, int n);

template <typename LLTYPE>
LLTYPE make_array_from_list(PyObject *list, int n)
{
    LLTYPE p = reinterpret_cast<LLTYPE>(make_array_from_list(list, n)) ;
    if ( !p ) throw py_exception();
    return p;
}

template <typename aTYPE>
PyObject* make_list( aTYPE p[], size_t n )
{
    PyObject *list = PyList_New(n);

    if (!list)
        return NULL;

    size_t i;
    for (i=0; i<n; i++) {
        PyObject *elem = pycap_new<aTYPE>( p[i] );
        PyList_SetItem(list, i, elem);
    }

    return list;
}

/*===----------------------------------------------------------------------===*/
/* Wrapper macros                                                             */
/*===----------------------------------------------------------------------===*/

/* The following wrapper macros define functions that wrap over LLVM-C APIs
 * of various signatures. Though they look hairy, they all follow some
 * conventions.
 */


/******************************************************************************
 ******************************************************************************
 *** PyCapsule Calls
 ******************************************************************************
 *****************************************************************************/

#define _wrap_none2none(func)                               \
static PyObject *                                           \
_w ## func(PyObject * self, PyObject * args)                \
{                                                           \
    LLVMPY_TRY                                              \
    if (!PyArg_ParseTuple(args, ""))                        \
        return NULL;                                        \
    func();                                                 \
    Py_RETURN_NONE;                                         \
    LLVMPY_CATCH_ALL                                        \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1)
 */
#define _wrap_obj2obj(func, intype1, outtype)           \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    intype1 arg1 = get_object_arg<intype1>(args);       \
                                                        \
    return pycap_new<outtype>( func( arg1 ) );          \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(int arg1)
 */
#define _wrap_int2obj(func, outtype)                    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    int arg1;                                           \
                                                        \
    if (!PyArg_ParseTuple(args, "i", &arg1))            \
        return NULL;                                    \
                                                        \
    return pycap_new<outtype>( func( arg1 ) );          \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2)
 */
#define _wrap_objobj2obj(func, intype1, intype2, outtype)\
static PyObject *                                        \
_w ## func (PyObject *self, PyObject *args)              \
{                                                        \
    LLVMPY_TRY                                           \
    PyObject *obj1, *obj2;                               \
                                                         \
    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))     \
        return NULL;                                     \
                                                         \
    const intype1 arg1 = pycap_get< intype1 > (obj1);    \
    const intype2 arg2 = pycap_get< intype2 > (obj2);    \
                                                         \
    return pycap_new<outtype>( func( arg1, arg2 ) );     \
    LLVMPY_CATCH_ALL                                     \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, intype2 arg2)
 */
#define _wrap_objobj2none(func, intype1, intype2)       \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    PyObject *obj1, *obj2;                              \
                                                        \
    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))    \
        return NULL;                                    \
                                                        \
    intype1 arg1 = pycap_get< intype1 > (obj1);         \
    intype2 arg2 = pycap_get< intype2 > (obj2);         \
                                                        \
    func (arg1, arg2);                                  \
    Py_RETURN_NONE;                                     \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, <unsigned/signed int> arg2)
 */
#define _wrap_objint2obj(func, intype1, outtype)        \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    PyObject *obj1;                                     \
    size_t arg2;                                        \
                                                        \
    if (!PyArg_ParseTuple(args, "OI", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);   \
                                                        \
    return pycap_new<outtype>( func( arg1, arg2 ) );    \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3)
 */
#define _wrap_objobjobj2obj(func, intype1, intype2, intype3, outtype)   \
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj2, *obj3;                                       \
                                                                        \
    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))            \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                   \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3 ) );              \
    LLVMPY_CATCH_ALL                                                    \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, intype2 arg2, intype3 arg3)
 */
#define _wrap_objobjobj2none(func, intype1, intype2, intype3)   \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj2, *obj3;                               \
                                                                \
    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))    \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype2 arg2 = pycap_get< intype2 > (obj2);           \
    const intype3 arg3 = pycap_get< intype3 > (obj3);           \
                                                                \
    func (arg1, arg2, arg3);                                    \
    Py_RETURN_NONE;                                             \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(<unsigned/signed int> arg1, intype2 arg2, intype3 arg3)
 */
#define _wrap_intobjobj2obj(func, intype2, intype3, outtype)    \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    size_t arg1;                                                \
    PyObject *obj2, *obj3;                                      \
                                                                \
    if (!PyArg_ParseTuple(args, "IOO", &arg1, &obj2, &obj3))    \
        return NULL;                                            \
                                                                \
    const intype2 arg2 = pycap_get< intype2 > (obj2);           \
    const intype3 arg3 = pycap_get< intype3 > (obj3);           \
                                                                \
    return pycap_new<outtype>( func( arg1, arg2, arg3 ) );      \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(enum_intype1 arg1, intype2 arg2, intype3 arg3)
 */
#define _wrap_enumobjobj2obj(func, intype1, intype2, intype3, outtype)    \
static PyObject *                                                         \
_w ## func (PyObject *self, PyObject *args)                               \
{                                                                         \
    LLVMPY_TRY                                                            \
    intype1 arg1;                                                         \
    PyObject *obj2, *obj3;                                                \
                                                                          \
    if (!PyArg_ParseTuple(args, "IOO", &arg1, &obj2, &obj3))              \
        return NULL;                                                      \
                                                                          \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                     \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                     \
                                                                          \
    return pycap_new<outtype>( func( arg1, arg2, arg3 ) );                \
    LLVMPY_CATCH_ALL                                                      \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(const char *s)
 */
#define _wrap_str2obj(func, outtype)                    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    const char *arg1;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "s", &arg1))            \
        return NULL;                                    \
                                                        \
    return pycap_new<outtype>( func( arg1 ) );          \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func()
 */
#define _wrap_none2obj(func, outtype)                   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    if (!PyArg_ParseTuple(args, ""))                    \
        return NULL;                                    \
                                                        \
    return pycap_new<outtype>( func() );                \
    LLVMPY_CATCH_ALL                                    \
}


/**
 * Wrap LLVM functions of the type
 * const char * func()
 */
 #define _wrap_none2str(func)                           \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    if (!PyArg_ParseTuple(args, ""))                    \
        return NULL;                                    \
    return PyUnicode_FromString(func());                \
    LLVMPY_CATCH_ALL                                    \
}


/**
 * Wrap LLVM functions of the type
 * const char *func(intype1 arg1)
 */
#define _wrap_obj2str(func, intype1)                    \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    const intype1 arg1 = get_object_arg<intype1>(args) ; \
    return PyUnicode_FromString( func (arg1));          \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1)
 */
#define _wrap_obj2none(func, intype1)                   \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    const intype1 arg1 = get_object_arg<intype1>(args) ; \
    func (arg1);                                        \
    Py_RETURN_NONE;                                     \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, const char *arg2)
 */
#define _wrap_objstr2none(func, intype1)                \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    PyObject *obj1;                                     \
    const char *arg2;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "Os", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    const intype1 arg1 = pycap_get< intype1 >( obj1 );  \
                                                        \
    func (arg1, arg2);                                  \
    Py_RETURN_NONE;                                     \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, const char *arg2)
 */
#define _wrap_objstr2obj(func, intype1, outtype)        \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    PyObject *obj1;                                     \
    const char *arg2;                                   \
                                                        \
    if (!PyArg_ParseTuple(args, "Os", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);   \
                                                        \
    return pycap_new<outtype>( func( arg1, arg2 ) );    \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, <unsigned/signed int> arg2)
 */
#define _wrap_objint2none(func, intype1)                \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    PyObject *obj1;                                     \
    int arg2;                                           \
                                                        \
    if (!PyArg_ParseTuple(args, "Oi", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);   \
                                                        \
    func (arg1, arg2);                                  \
    Py_RETURN_NONE;                                     \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, enum_intype2 arg2)
 */
#define _wrap_objenum2none(func, intype1, intype2)      \
static PyObject *                                       \
_w ## func (PyObject *self, PyObject *args)             \
{                                                       \
    LLVMPY_TRY                                          \
    intype2 arg2;                                       \
    PyObject *obj1;                                     \
                                                        \
    if (!PyArg_ParseTuple(args, "Oi", &obj1, &arg2))    \
        return NULL;                                    \
                                                        \
    const intype1 arg1 = pycap_get< intype1 >( obj1 );  \
                                                        \
    func (arg1, arg2);                                  \
    Py_RETURN_NONE;                                     \
    LLVMPY_CATCH_ALL                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, const char *arg3)
 */
#define _wrap_objobjstr2obj(func, intype1, intype2, outtype)    \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj2;                                      \
    const char *arg3;                                           \
                                                                \
    if (!PyArg_ParseTuple(args, "OOs", &obj1, &obj2, &arg3))    \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype2 arg2 = pycap_get< intype2 > (obj2);           \
                                                                \
    return pycap_new<outtype> ( func (arg1, arg2, arg3));       \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, int arg3)
 */
#define _wrap_objobjint2obj(func, intype1, intype2, outtype)    \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj2;                                      \
    int arg3;                                                   \
                                                                \
    if (!PyArg_ParseTuple(args, "OOi", &obj1, &obj2, &arg3))    \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype2 arg2 = pycap_get< intype2 > (obj2);           \
                                                                \
    return pycap_new<outtype>( func( arg1, arg2, arg3 ) ) ;     \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, unsigned long long arg3)
 */
#define _wrap_objobjull2obj(func, intype1, intype2, outtype)    \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj2;                                      \
    unsigned long long arg3;                                    \
                                                                \
    if (!PyArg_ParseTuple(args, "OOK", &obj1, &obj2, &arg3))    \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype2 arg2 = pycap_get< intype2 > (obj2);           \
                                                                \
    return pycap_new<outtype>( func( arg1, arg2, arg3 ) ) ;     \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, <unsigned/signed int> arg2, <unsigned/signed int> arg3)
 */
#define _wrap_objintint2none(func, intype1)                     \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1;                                             \
    int arg2, arg3;                                             \
                                                                \
    if (!PyArg_ParseTuple(args, "Oii", &obj1, &arg2, &arg3))    \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
                                                                \
    func (arg1, arg2, arg3);                                    \
    Py_RETURN_NONE;                                             \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, <unsigned/signed int> arg2, enum_intype3 arg3)
 */
#define _wrap_objintenum2none(func, intype1, intype3)         \
static PyObject *                                             \
_w ## func (PyObject *self, PyObject *args)                   \
{                                                             \
    LLVMPY_TRY                                                \
    PyObject *obj1;                                           \
    int arg2;                                                 \
    intype3 arg3;                                             \
                                                              \
    if (!PyArg_ParseTuple(args, "Oii", &obj1, &arg2, &arg3))  \
        return NULL;                                          \
                                                              \
    const intype1 arg1 = pycap_get< intype1 >( obj1 );        \
                                                              \
    func (arg1, arg2, arg3);                                  \
    Py_RETURN_NONE;                                           \
    LLVMPY_CATCH_ALL                                          \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, const char *arg2, intype3 arg3)
 */
#define _wrap_objstrobj2obj(func, intype1, intype3, outtype)    \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj3;                                      \
    const char *arg2;                                           \
                                                                \
    if (!PyArg_ParseTuple(args, "OsO", &obj1, &arg2, &obj3))    \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype3 arg3 = pycap_get< intype3 > (obj3);           \
                                                                \
    return pycap_new<outtype>( func( arg1, arg2, arg3 ) );      \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, const char *arg2, intype3 arg3)
 */
#define _wrap_objstrobj2none(func, intype1, intype3)            \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj3;                                      \
    const char *arg2;                                           \
                                                                \
    if (!PyArg_ParseTuple(args, "OsO", &obj1, &arg2, &obj3))    \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype3 arg3 = pycap_get< intype3 > (obj3);           \
                                                                \
    func(arg1, arg2, arg3);                                     \
                                                                \
    Py_RETURN_NONE;                                             \
    LLVMPY_CATCH_ALL                                            \
}


/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, int arg3, const char *arg4)
 */
#define _wrap_objobjintstr2obj(func, intype1, intype2, outtype)       \
static PyObject *                                                     \
_w ## func (PyObject *self, PyObject *args)                           \
{                                                                     \
    LLVMPY_TRY                                                        \
    PyObject *obj1, *obj2;                                            \
    int arg3;                                                         \
    const char *arg4;                                                 \
                                                                      \
    if (!PyArg_ParseTuple(args, "OOis", &obj1, &obj2, &arg3, &arg4))  \
        return NULL;                                                  \
                                                                      \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                 \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                 \
                                                                      \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4 ) ) ;     \
    LLVMPY_CATCH_ALL                                                  \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3, int arg3, const char *arg4)
 */
#define _wrap_objobjobjintstr2obj(func, intype1, intype2, intype3, outtype) \
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
  LLVMPY_TRY                                                            \
  PyObject *obj1, *obj2, *obj3;                                         \
  int arg4;                                                             \
  const char *arg5;                                                     \
                                                                        \
  if (!PyArg_ParseTuple(args, "OOOis", &obj1, &obj2, &obj3, &arg4,      \
                        &arg5))                                         \
    return NULL;                                                        \
                                                                        \
  const intype1 arg1 = pycap_get< intype1 > (obj1);                     \
  const intype2 arg2 = pycap_get< intype2 > (obj2);                     \
  const intype3 arg3 = pycap_get< intype3 > (obj3);                     \
                                                                        \
  return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5 ) ) ;   \
  LLVMPY_CATCH_ALL                                                      \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, const char *arg4)
 */
#define _wrap_objobjobjstr2obj(func, intype1, intype2, intype3, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj2, *obj3;                                       \
    const char *arg4;                                                   \
                                                                        \
    if (!PyArg_ParseTuple(args, "OOOs", &obj1, &obj2, &obj3, &arg4))    \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                   \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4 ) );        \
    LLVMPY_CATCH_ALL                                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, const char *arg3, <unsigned/signed int> arg4)
 */
#define _wrap_objobjstrint2obj(func, intype1, intype2, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj2;                                              \
    const char *arg3;                                                   \
    int arg4;                                                           \
                                                                        \
    if (!PyArg_ParseTuple(args, "OOsi", &obj1, &obj2, &arg3, &arg4))    \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4 ) );        \
    LLVMPY_CATCH_ALL                                                    \
}



/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, <unsigned/signed int> arg3, const char *arg4, <unsigned/signed int> arg5)
 */
#define _wrap_objobjintstrint2obj(func, intype1, intype2, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj2;                                              \
    int arg3;                                                           \
    const char *arg4;                                                   \
    int arg5;                                                           \
                                                                        \
    if (!PyArg_ParseTuple(args, "OOisi", &obj1, &obj2, &arg3, &arg4, &arg5))    \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5 ) );  \
    LLVMPY_CATCH_ALL                                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, const char *arg2, <unsigned/signed int> arg3)
 */
#define _wrap_objstrint2obj(func, intype1, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1;                                                     \
    const char *arg2;                                                   \
    int arg3;                                                           \
                                                                        \
    if (!PyArg_ParseTuple(args, "Osi", &obj1, &arg2, &arg3))            \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3 ) );              \
    LLVMPY_CATCH_ALL                                                    \
}


/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3, const char *arg4, <unsigned/signed int> arg5)
 */
#define _wrap_objobjobjstrint2obj(func, intype1, intype2, intype3, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj2, *obj3;                                       \
    const char *arg4;                                                   \
    int arg5;                                                           \
                                                                        \
    if (!PyArg_ParseTuple(args, "OOOsi", &obj1, &obj2, &obj3, &arg4, &arg5))    \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                   \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5 ) );  \
    LLVMPY_CATCH_ALL                                                    \
}




/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3, <unsigned/signed int> arg4, const char *arg5, <unsigned/signed int> arg6)
 */
#define _wrap_objobjobjintstrint2obj(func, intype1, intype2, intype3, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj2, *obj3;                                       \
    int arg4;                                                           \
    const char *arg5;                                                   \
    int arg6;                                                           \
                                                                        \
    if (!PyArg_ParseTuple(args, "OOOisi", &obj1, &obj2, &obj3, &arg4, &arg5, &arg6))    \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                   \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5, arg6 ) );\
    LLVMPY_CATCH_ALL                                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, intype4, const char *arg5, <unsigned/signed int> arg6)
 */
#define _wrap_objobjobjobjstrint2obj(func, intype1, intype2, intype3, intype4, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj2, *obj3, *obj4;                                \
    const char *arg5;                                                   \
    int arg6;                                                           \
                                                                        \
    if (!PyArg_ParseTuple(args, "OOOOsi", &obj1, &obj2, &obj3, &obj4, &arg5, &arg6))   \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                   \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                   \
    const intype4 arg4 = pycap_get< intype4 > (obj4);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5, arg6 ) );     \
    LLVMPY_CATCH_ALL                                                    \
}


/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, const char* arg2, intype3 arg3, intype4, const char *arg5, <unsigned/signed int> arg6)
 */
#define _wrap_objstrobjobjstrint2obj(func, intype1, intype3, intype4, outtype)\
static PyObject *                                                       \
_w ## func (PyObject *self, PyObject *args)                             \
{                                                                       \
    LLVMPY_TRY                                                          \
    PyObject *obj1, *obj3, *obj4;                                       \
    const char *arg2;                                                   \
    const char *arg5;                                                   \
    int arg6;                                                           \
                                                                        \
    if (!PyArg_ParseTuple(args, "OsOOsi", &obj1, &arg2, &obj3, &obj4, &arg5, &arg6))   \
        return NULL;                                                    \
                                                                        \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                   \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                   \
    const intype4 arg4 = pycap_get< intype4 > (obj4);                   \
                                                                        \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5, arg6 ) ); \
    LLVMPY_CATCH_ALL                                                    \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, <unsigned/signed int> arg4)
 */
#define _wrap_objobjobjint2obj(func, intype1, intype2, intype3, outtype)    \
static PyObject *                                                           \
_w ## func (PyObject *self, PyObject *args)                                 \
{                                                                           \
    LLVMPY_TRY                                                              \
    PyObject *obj1, *obj2, *obj3;                                           \
    int arg4;                                                               \
                                                                            \
    if (!PyArg_ParseTuple(args, "OOOi", &obj1, &obj2, &obj3, &arg4))        \
        return NULL;                                                        \
                                                                            \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                       \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                       \
    const intype3 arg3 = pycap_get< intype3 > (obj3);                       \
                                                                            \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4 ) );            \
    LLVMPY_CATCH_ALL                                                        \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, intype arg4)
 */
#define _wrap_objobjobjobj2obj(func, intype1, intype2, intype3, \
        intype4, outtype)                                       \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj2, *obj3, *obj4;                        \
                                                                \
    if (!PyArg_ParseTuple(args, "OOOO", &obj1, &obj2, &obj3, &obj4)) \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype2 arg2 = pycap_get< intype2 > (obj2);           \
    const intype3 arg3 = pycap_get< intype3 > (obj3);           \
    const intype4 arg4 = pycap_get< intype4 > (obj4);           \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4 ) );\
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 arg3, intype arg4, const char *arg5)
 */
#define _wrap_objobjobjobjstr2obj(func, intype1, intype2, intype3, \
        intype4, outtype)\
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj2, *obj3, *obj4;                        \
    const char *arg5;                                           \
                                                                \
    if (!PyArg_ParseTuple(args, "OOOOs", &obj1, &obj2, &obj3, &obj4, &arg5))        \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype2 arg2 = pycap_get< intype2 > (obj2);           \
    const intype3 arg3 = pycap_get< intype3 > (obj3);           \
    const intype4 arg4 = pycap_get< intype4 > (obj4);           \
                                                                \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5 ) );\
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, enum_intype2 arg2, intype3 arg3, intype4 arg4, const char *arg5)
 */
#define _wrap_objenumobjobjstr2obj(func, intype1, intype2, intype3, \
        intype4, outtype) \
static PyObject *                                               \
_w ## func (PyObject *self, PyObject *args)                     \
{                                                               \
    LLVMPY_TRY                                                  \
    PyObject *obj1, *obj3, *obj4;                               \
    intype2 arg2 ;                                              \
    const char *arg5;                                           \
                                                                \
    if (!PyArg_ParseTuple(args, "OiOOs", &obj1, &arg2, &obj3, &obj4, &arg5)) \
        return NULL;                                            \
                                                                \
    const intype1 arg1 = pycap_get< intype1 > (obj1);           \
    const intype3 arg3 = pycap_get< intype3 > (obj3);           \
    const intype4 arg4 = pycap_get< intype4 > (obj4);           \
                                                                \
    return pycap_new<outtype>( func( arg1, arg2, arg3, arg4, arg5 ) ); \
    LLVMPY_CATCH_ALL                                            \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 *arg2v, unsigned arg2n)
 * where arg2v is an array of intype2 elements, arg2n in length.
 */
#define _wrap_objlist2obj(func, intype1, intype2, outtype)       \
static PyObject *                                                \
_w ## func (PyObject *self, PyObject *args)                      \
{                                                                \
    LLVMPY_TRY                                                   \
    PyObject *obj1, *obj2;                                       \
                                                                 \
    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))             \
        return NULL;                                             \
                                                                 \
    const intype1 arg1 = pycap_get< intype1 >( obj1 );           \
    const size_t arg2n = PyList_Size(obj2);                      \
    intype2 *arg2v = make_array_from_list< intype2 *>(obj2, arg2n); \
                                                                 \
    outtype ret = func (arg1, arg2v, arg2n);                     \
    delete [] arg2v ;                                            \
    return pycap_new<outtype>( ret );                            \
    LLVMPY_CATCH_ALL                                             \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 *arg1v, unsigned arg1n, int arg2)
 * where arg1v is an array of intype1 elements, arg1n in length.
 */
#define _wrap_listint2obj(func, intype1, outtype)                \
static PyObject *                                                \
_w ## func (PyObject *self, PyObject *args)                      \
{                                                                \
    LLVMPY_TRY                                                   \
    PyObject *obj1;                                              \
    int arg2;                                                    \
                                                                 \
    if (!PyArg_ParseTuple(args, "Oi", &obj1, &arg2))             \
        return NULL;                                             \
                                                                 \
    const size_t arg1n = PyList_Size(obj1);                      \
    intype1 *arg1v = make_array_from_list< intype1 *>(obj1, arg1n); \
                                                                 \
    outtype ret = func (arg1v, arg1n, arg2);                     \
    delete [] arg1v;                                             \
    return pycap_new<outtype>( ret );                            \
    LLVMPY_CATCH_ALL                                             \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 *arg1v, unsigned arg1n)
 * where arg1v is an array of intype1 elements, arg1n in length.
 */
#define _wrap_list2obj(func, intype1, outtype)                   \
static PyObject *                                                \
_w ## func (PyObject *self, PyObject *args)                      \
{                                                                \
    LLVMPY_TRY                                                   \
    PyObject *obj1;                                              \
                                                                 \
    if (!PyArg_ParseTuple(args, "O", &obj1))                     \
        return NULL;                                             \
                                                                 \
    const size_t arg1n = PyList_Size(obj1);                      \
    intype1 *arg1v = make_array_from_list< intype1 *>(obj1, arg1n); \
                                                                 \
    outtype ret = func (arg1v, arg1n);                           \
    delete [] arg1v;                                             \
    return pycap_new<outtype>( ret );                            \
    LLVMPY_CATCH_ALL                                             \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 *arg2v, unsigned arg2n, int arg3)
 * where arg2v is an array of intype2 elements, arg2n in length.
 */
#define _wrap_objlistint2obj(func, intype1, intype2, outtype)    \
static PyObject *                                                \
_w ## func (PyObject *self, PyObject *args)                      \
{                                                                \
    LLVMPY_TRY                                                   \
    PyObject *obj1, *obj2;                                       \
    int arg3;                                                    \
                                                                 \
    if (!PyArg_ParseTuple(args, "OOi", &obj1, &obj2, &arg3))     \
        return NULL;                                             \
                                                                 \
    intype1 arg1 = pycap_get< intype1 >( obj1 );                 \
    const size_t arg2n = PyList_Size(obj2);                      \
    intype2 *arg2v = make_array_from_list< intype2 *>(obj2, arg2n);       \
                                                                 \
    outtype ret = func (arg1, arg2v, arg2n, arg3);               \
    delete [] arg2v ;                                            \
    return pycap_new<outtype>( ret );                            \
    LLVMPY_CATCH_ALL                                             \
}


/**
 * Wrap LLVM functions of the type
 * void func(intype1 arg1, intype2 *arg2v, unsigned arg2n, int arg3)
 * where arg2v is an array of intype2 elements, arg2n in length.
 */
#define _wrap_objlistint2none(func, intype1, intype2)            \
static PyObject *                                                \
_w ## func (PyObject *self, PyObject *args)                      \
{                                                                \
    LLVMPY_TRY                                                   \
    PyObject *obj1, *obj2;                                       \
    int arg3;                                                    \
                                                                 \
    if (!PyArg_ParseTuple(args, "OOi", &obj1, &obj2, &arg3))     \
        return NULL;                                             \
                                                                 \
    const intype1 arg1 = pycap_get< intype1 >( obj1 );           \
    const size_t arg2n = PyList_Size(obj2);                      \
    intype2 *arg2v = make_array_from_list< intype2 *>(obj2, arg2n); \
                                                                 \
    func (arg1, arg2v, arg2n, arg3);                             \
    delete [] arg2v ;                                            \
    Py_RETURN_NONE;                                              \
    LLVMPY_CATCH_ALL                                             \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, int arg2, intype3 *arg3v, unsigned arg3n)
 * where arg3v is an array of intype3 elements, arg3n in length.
 */
#define _wrap_objintlist2obj(func, intype1, intype3, outtype)    \
static PyObject *                                                \
_w ## func (PyObject *self, PyObject *args)                      \
{                                                                \
    LLVMPY_TRY                                                   \
    PyObject *obj1, *obj3;                                       \
    int arg2;                                                    \
                                                                 \
    if (!PyArg_ParseTuple(args, "OiO", &obj1, &arg2, &obj3))     \
        return NULL;                                             \
                                                                 \
    const intype1 arg1 = pycap_get< intype1 >( obj1 );           \
    const size_t arg3n = PyList_Size(obj3);                      \
    intype3 *arg3v = make_array_from_list< intype3 *>(obj3, arg3n); \
                                                                 \
    outtype ret = func (arg1, arg2, arg3v, arg3n);               \
    delete [] arg3v ;                                            \
    return pycap_new<outtype>( ret );                            \
    LLVMPY_CATCH_ALL                                             \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 *arg3v, unsigned arg3n)
 * where arg3v is an array of intype3 elements, arg3n in length.
 */
#define _wrap_objobjlist2obj(func, intype1, intype2, intype3, outtype)      \
static PyObject *                                                           \
_w ## func (PyObject *self, PyObject *args)                                 \
{                                                                           \
    LLVMPY_TRY                                                              \
    PyObject *obj1, *obj2, *obj3;                                           \
                                                                            \
    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))                \
        return NULL;                                                        \
                                                                            \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                       \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                       \
    const size_t arg3n = PyList_Size(obj3);                                 \
    intype3 *arg3v = make_array_from_list< intype3 *>(obj3, arg3n);         \
                                                                            \
    outtype ret = func (arg1, arg2, arg3v, arg3n);                          \
    delete [] arg3v ;                                                       \
    return pycap_new<outtype>( ret );                                       \
    LLVMPY_CATCH_ALL                                                        \
}

/**
 * Wrap LLVM functions of the type
 * outtype func(intype1 arg1, intype2 arg2, intype3 *arg3v, unsigned arg3n, const char *arg4)
 * where arg3v is an array of intype3 elements, arg3n in length.
 */
#define _wrap_objobjliststr2obj(func, intype1, intype2, intype3, outtype)   \
static PyObject *                                                           \
_w ## func (PyObject *self, PyObject *args)                                 \
{                                                                           \
    LLVMPY_TRY                                                              \
    PyObject *obj1, *obj2, *obj3;                                           \
    const char *arg4;                                                       \
                                                                            \
    if (!PyArg_ParseTuple(args, "OOOs", &obj1, &obj2, &obj3, &arg4))        \
        return NULL;                                                        \
                                                                            \
    const intype1 arg1 = pycap_get< intype1 > (obj1);                       \
    const intype2 arg2 = pycap_get< intype2 > (obj2);                       \
    const size_t arg3n = PyList_Size(obj3);                                 \
    intype3 *arg3v = make_array_from_list< intype3 *>(obj3, arg3n);         \
                                                                            \
    outtype ret = func (arg1, arg2, arg3v, arg3n, arg4);                    \
    delete [] arg3v ;                                                       \
    return pycap_new<outtype>( ret );                                       \
    LLVMPY_CATCH_ALL                                                        \
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
    LLVMPY_TRY                                                      \
    intype1 arg1 = get_object_arg<intype1>(args);                   \
                                                                    \
    const char *val = func (arg1);                                  \
    PyObject *ret = PyUnicode_FromString(val);                      \
    LLVMDisposeMessage(const_cast<char*>(val));                     \
    return ret;                                                     \
    LLVMPY_CATCH_ALL                                                \
}


#endif /* LLVM_PY_WRAP_H */
