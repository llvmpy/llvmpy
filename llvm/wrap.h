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
        PyErr_SetString(PyExc_RuntimeError,              \
                        "Unknown exception");            \
        return NULL;                                     \
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



#endif /* LLVM_PY_WRAP_H */
