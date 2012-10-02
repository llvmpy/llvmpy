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

/* our includes */
#include "wrap.h"
#include "extra.h"



// Python include
#include "Python.h"

/* LLVM includes */
#include "llvm-c/Analysis.h"
#include "llvm-c/Transforms/Scalar.h"
#include "llvm-c/ExecutionEngine.h"
#include "llvm-c/Target.h"
#include "llvm-c/Transforms/IPO.h"

#include "llvm/Support/CommandLine.h"
#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
    #include "llvm-c/Linker.h"
#else
    typedef unsigned int LLVMLinkerMode;
#endif

/* Compatibility with Python 2.4: Py_ssize_t is not available. */
#ifndef PY_SSIZE_T_MAX
typedef int Py_ssize_t;
#endif


// explicit specializations
template <> PyObject* pycap_new<int>(int i)
{
    return PyLong_FromLong(static_cast<long>(i));
}

template <> PyObject* pycap_new<unsigned int>(unsigned int i)
{
    return PyLong_FromLong(static_cast<long>(i));
}

template <> PyObject* pycap_new<unsigned long>(unsigned long i)
{
    return PyLong_FromLong(static_cast<unsigned long>(i));
}

template <> PyObject* pycap_new<LLVMTypeKind>(LLVMTypeKind i)
{
    return PyLong_FromLong(static_cast<unsigned long>(i));
}

template <> PyObject* pycap_new<LLVMLinkage>(LLVMLinkage i)
{
    return PyLong_FromLong(static_cast<unsigned long>(i));
}

template <> PyObject* pycap_new<LLVMVisibility>(LLVMVisibility i)
{
    return PyLong_FromLong(static_cast<unsigned long>(i));
}

template <> PyObject* pycap_new<LLVMByteOrdering>(LLVMByteOrdering i)
{
    return PyLong_FromLong(static_cast<unsigned long>(i));
}

template <> PyObject* pycap_new<unsigned long long>(unsigned long long ull)
{
    return PyLong_FromUnsignedLongLong(ull);
}

template <> PyObject* pycap_new<long long>(long long ll)
{
    return PyLong_FromLongLong(ll);
}

// Wrappers

// Make Wrapper - static instantion to call matching LLVM python wrapper
#define MW( llvm_func_name )                                \
static PyObject *                                           \
_w ## llvm_func_name( PyObject *self, PyObject *args )      \
{                                                           \
    return WF( llvm_func_name, self, args ) ;               \
}                                                           \

// Make Specialized Wrapper - static instantion to call
// matching specilized LLVM python wrapper
#define MSW( llvm_func_name, special_func_str )             \
static PyObject *                                           \
_w ## llvm_func_name( PyObject *self, PyObject *args )      \
{                                                           \
    return special_func_str( llvm_func_name, self, args ) ; \
}                                                           \

// Python wrappers for various LLVM functions and return values

// they all have the same name, WF, allowing a single macro to write a wrapper

// but they have different function sigatures
// matching the llvm function signature
// and the wrapper return type

static PyObject* WF( void (&llvm_func)( ),
                     PyObject * self, PyObject * args)
{
    LLVMPY_TRY
    if (!PyArg_ParseTuple(args, "")) return NULL;
    llvm_func();
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

static PyObject* WF( const char* (&llvm_func)( ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    if (!PyArg_ParseTuple(args, "")) return NULL;
    return PyUnicode_FromString(llvm_func());
    LLVMPY_CATCH_ALL
}

template <class intype1 >
PyObject* WF( void (&llvm_func)( intype1 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    const intype1 arg1 = get_object_arg<intype1>(args) ;
    llvm_func(arg1);
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

template <class intype1 >
PyObject* WF( char* (&llvm_func)( intype1 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    const intype1 arg1 = get_object_arg<intype1>(args) ;
    return PyUnicode_FromString( llvm_func(arg1));
    LLVMPY_CATCH_ALL
}

template <class intype1 >
PyObject* WF( const char* (&llvm_func)( intype1 ),
                     PyObject *self, PyObject *args )
{
    // call the version returning "char*"
    typedef char* (&tifunc)( intype1 ) ;
    tifunc ifunc = reinterpret_cast<tifunc>( llvm_func ) ;
    return WF( ifunc, self, args ) ;
}

// Wrap and Dispose - unique from WF( char* ()( intype )..
template <class intype1 >
PyObject* WD( char* (&llvm_func)( intype1 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    intype1 arg1 = get_object_arg<intype1>(args);
    char *val = llvm_func(arg1);
    PyObject *ret = PyUnicode_FromString(val);
    LLVMDisposeMessage(val);
    return ret;
    LLVMPY_CATCH_ALL
}

template <class intype1, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    const intype1 arg1 = get_object_arg<intype1>(args) ;
    llvm_func(arg1);
    return pycap_new<outtype>( llvm_func( arg1 ) );
    LLVMPY_CATCH_ALL
}

template <class outtype >
PyObject* WF( outtype (&llvm_func)( unsigned int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    unsigned int arg1;

    if (!PyArg_ParseTuple(args, "i", &arg1)) return NULL;

    return pycap_new<outtype>( llvm_func( arg1 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, intype2 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;

    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);

    return pycap_new<outtype>( llvm_func( arg1, arg2 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2>
PyObject* WF( void (&llvm_func)( intype1, intype2 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;

    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2)) return NULL;

    intype1 arg1 = pycap_get< intype1 > (obj1);
    intype2 arg2 = pycap_get< intype2 > (obj2);

    llvm_func(arg1, arg2);
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, unsigned int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    unsigned int arg2;

    if (!PyArg_ParseTuple(args, "OI", &obj1, &arg2)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);

    return pycap_new<outtype>( llvm_func( arg1, arg2 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3;

    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3>
PyObject* WF( void (&llvm_func)( intype1, intype2, intype3 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3;

    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    llvm_func(arg1, arg2, arg3);
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

// collides with other specialized version..
template <class intype1, class intype2, class intype3, class outtype>
PyObject* WF_enum1( outtype (&llvm_func)( intype1, intype2, intype3 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    intype1 arg1;
    PyObject *obj2, *obj3;

    if (!PyArg_ParseTuple(args, "IOO", &arg1, &obj2, &obj3)) return NULL;

    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3 ) );
    LLVMPY_CATCH_ALL
}

template <class outtype >
PyObject* WF( outtype (&llvm_func)( const char* ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    const char *arg1;

    if (!PyArg_ParseTuple(args, "s", &arg1)) return NULL;

    return pycap_new<outtype>( llvm_func( arg1 ) );
    LLVMPY_CATCH_ALL
}

template <class outtype >
PyObject* WF( outtype (&llvm_func)( void ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    if (!PyArg_ParseTuple(args, "")) return NULL;

    return pycap_new<outtype>( llvm_func() );
    LLVMPY_CATCH_ALL
}

template <class intype1 >
PyObject* WF( void (&llvm_func)( intype1, const char * ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    const char *arg2;

    if (!PyArg_ParseTuple(args, "Os", &obj1, &arg2)) return NULL;

    const intype1 arg1 = pycap_get< intype1 >( obj1 );

    llvm_func(arg1, arg2);
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

template <class intype1, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, const char* ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    const char *arg2;

    if (!PyArg_ParseTuple(args, "Os", &obj1, &arg2)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);

    return pycap_new<outtype>( llvm_func( arg1, arg2 ) );
    LLVMPY_CATCH_ALL
}

// collides with other specialized version..
template <class intype1 >
PyObject* WF_int2( void (&llvm_func)( intype1, int ),
                   PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    int arg2;

    if (!PyArg_ParseTuple(args, "Oi", &obj1, &arg2)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);

    llvm_func(arg1, arg2);
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

// call the int version from unsigned int
template <typename intype1 >
PyObject* WF_int2( void (&llvm_func)( intype1, unsigned int ),
                     PyObject *self, PyObject *args )
{
    typedef void(&tifunc)( intype1, int ) ;
    tifunc ifunc = reinterpret_cast<tifunc>( llvm_func ) ;
    return WF_int2( ifunc, self, args ) ;
}

// call the int version from enum
template <class intype1, class intype2>
PyObject* WF_enum2( void (&llvm_func)( intype1, intype2 ),
                     PyObject *self, PyObject *args )
{
    typedef void(&tifunc)( intype1, int ) ;
    tifunc ifunc = reinterpret_cast<tifunc>( llvm_func ) ;
    return WF_int2( ifunc, self, args ) ;
}

template <class intype1, class intype2, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, intype2, const char* ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;
    const char *arg3;

    if (!PyArg_ParseTuple(args, "OOs", &obj1, &obj2, &arg3))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);

    return pycap_new<outtype> ( llvm_func(arg1, arg2, arg3));
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, intype2, unsigned int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;
    unsigned int arg3;

    if (!PyArg_ParseTuple(args, "OOi", &obj1, &obj2, &arg3)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3 ) ) ;
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, intype2, unsigned long long ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;
    unsigned long long arg3;

    if (!PyArg_ParseTuple(args, "OOK", &obj1, &obj2, &arg3)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3 ) ) ;
    LLVMPY_CATCH_ALL
}

template <class intype1>
PyObject* WF( void (&llvm_func)( intype1, unsigned int, unsigned int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    int arg2, arg3;

    if (!PyArg_ParseTuple(args, "Oii", &obj1, &arg2, &arg3)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);

    llvm_func (arg1, arg2, arg3);
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype3>
PyObject* WF( void (&llvm_func)( intype1, unsigned int, intype3 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    unsigned int arg2;
    intype3 arg3;

    if (!PyArg_ParseTuple(args, "Oii", &obj1, &arg2, &arg3)) return NULL;

    const intype1 arg1 = pycap_get< intype1 >( obj1 );

    llvm_func( arg1, arg2, arg3);
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype3, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, const char*, intype3 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj3;
    const char *arg2;

    if (!PyArg_ParseTuple(args, "OsO", &obj1, &arg2, &obj3)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3 ) );
    LLVMPY_CATCH_ALL
}


template <class intype1, class intype3>
PyObject* WF( void (&llvm_func)( intype1, const char*, intype3 ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj3;
    const char *arg2;

    if (!PyArg_ParseTuple(args, "OsO", &obj1, &arg2, &obj3)) return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    llvm_func(arg1, arg2, arg3);

    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, unsigned int, const char*),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;
    unsigned int arg3;
    const char *arg4;

    if (!PyArg_ParseTuple(args, "OOis", &obj1, &obj2, &arg3, &arg4))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4 ) ) ;
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3, unsigned int, const char*),
                     PyObject *self, PyObject *args )
{
  LLVMPY_TRY
  PyObject *obj1, *obj2, *obj3;
  unsigned int arg4;
  const char *arg5;

  if (!PyArg_ParseTuple(args, "OOOis", &obj1, &obj2, &obj3, &arg4,
                        &arg5))
    return NULL;

  const intype1 arg1 = pycap_get< intype1 > (obj1);
  const intype2 arg2 = pycap_get< intype2 > (obj2);
  const intype3 arg3 = pycap_get< intype3 > (obj3);

  return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4, arg5 ) ) ;
  LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3, const char*),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3;
    const char *arg4;

    if (!PyArg_ParseTuple(args, "OOOs", &obj1, &obj2, &obj3, &arg4))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, unsigned int, const char*, int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;
    unsigned int arg3;
    const char *arg4;
    int arg5;

    if (!PyArg_ParseTuple(args, "OOisi", &obj1, &obj2, &arg3, &arg4, &arg5))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4, arg5 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, const char*, int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    const char *arg2;
    int arg3;

    if (!PyArg_ParseTuple(args, "Osi", &obj1, &arg2, &arg3))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3, unsigned int,
                                    const char*, int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3;
    unsigned int arg4;
    const char *arg5;
    int arg6;

    if (!PyArg_ParseTuple(args, "OOOisi", &obj1, &obj2, &obj3, &arg4, &arg5, &arg6))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4, arg5, arg6 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class intype4,
    class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3, intype4,
                                    const char*, int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3, *obj4;
    const char *arg5;
    int arg6;

    if (!PyArg_ParseTuple(args, "OOOOsi", &obj1, &obj2, &obj3, &obj4, &arg5, &arg6))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);
    const intype4 arg4 = pycap_get< intype4 > (obj4);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4, arg5, arg6 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype3, class intype4, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, const char*, intype3, intype4,
                                    const char*, int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj3, *obj4;
    const char *arg2;
    const char *arg5;
    int arg6;

    if (!PyArg_ParseTuple(args, "OsOOsi", &obj1, &arg2, &obj3, &obj4, &arg5, &arg6))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype3 arg3 = pycap_get< intype3 > (obj3);
    const intype4 arg4 = pycap_get< intype4 > (obj4);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4, arg5, arg6 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3, unsigned int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3;
    unsigned int arg4;

    if (!PyArg_ParseTuple(args, "OOOi", &obj1, &obj2, &obj3, &arg4))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class intype4, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3, intype4),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3, *obj4;

    if (!PyArg_ParseTuple(args, "OOOO", &obj1, &obj2, &obj3, &obj4))
        return NULL ;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);
    const intype4 arg4 = pycap_get< intype4 > (obj4);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class intype4, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3, intype4, const char *),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3, *obj4;
    const char *arg5;

    if (!PyArg_ParseTuple(args, "OOOOs", &obj1, &obj2, &obj3, &obj4, &arg5))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const intype3 arg3 = pycap_get< intype3 > (obj3);
    const intype4 arg4 = pycap_get< intype4 > (obj4);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4, arg5 ) );
    LLVMPY_CATCH_ALL
}

// collides with other specialized version..
template <class intype1, class intype2, class intype3, class intype4, class outtype>
PyObject* WF_enum2_char4( outtype (&llvm_func)( intype1, intype2, intype3, intype4, const char *),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj3, *obj4;
    intype2 arg2 ;
    const char *arg5;

    if (!PyArg_ParseTuple(args, "OiOOs", &obj1, &arg2, &obj3, &obj4, &arg5))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype3 arg3 = pycap_get< intype3 > (obj3);
    const intype4 arg4 = pycap_get< intype4 > (obj4);

    return pycap_new<outtype>( llvm_func( arg1, arg2, arg3, arg4, arg5 ) );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, intype2*, unsigned int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;

    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 >( obj1 );
    const unsigned int arg2n = PyList_Size(obj2);
    intype2 *arg2v = make_array_from_list< intype2 *>(obj2, arg2n);

    outtype ret = llvm_func(arg1, arg2v, arg2n);
    delete [] arg2v ;

    return pycap_new<outtype>( ret );
    LLVMPY_CATCH_ALL
}

template <class intype1, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1*, unsigned int, int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;
    int arg2;

    if (!PyArg_ParseTuple(args, "Oi", &obj1, &arg2))
        return NULL;

    const size_t arg1n = PyList_Size(obj1);
    intype1 *arg1v = make_array_from_list< intype1 *>(obj1, arg1n);

    outtype ret = llvm_func(arg1v, arg1n, arg2);
    delete [] arg1v;

    return pycap_new<outtype>( ret );

    LLVMPY_CATCH_ALL
}

template <class intype1, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1*, unsigned int ),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1;

    if (!PyArg_ParseTuple(args, "O", &obj1)) return NULL;

    const size_t arg1n = PyList_Size(obj1);
    intype1 *arg1v = make_array_from_list< intype1 *>(obj1, arg1n);

    outtype ret = llvm_func(arg1v, arg1n);
    delete [] arg1v;

    return pycap_new<outtype>( ret );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype4, class outtype >
PyObject* WF( outtype (&llvm_func)( intype1, intype2*, unsigned int, intype4),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;
    int arg3;

    if (!PyArg_ParseTuple(args, "OOi", &obj1, &obj2, &arg3)) return NULL;

    intype1 arg1 = pycap_get< intype1 >( obj1 );
    const size_t arg2n = PyList_Size(obj2);
    intype2 *arg2v = make_array_from_list< intype2 *>(obj2, arg2n);

    outtype ret = llvm_func(arg1, arg2v, arg2n, arg3);
    delete [] arg2v ;

    return pycap_new<outtype>( ret );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2>
PyObject* WF( void (&llvm_func)( intype1, intype2*, unsigned int, int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;
    int arg3;

    if (!PyArg_ParseTuple(args, "OOi", &obj1, &obj2, &arg3))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 >( obj1 );
    const size_t arg2n = PyList_Size(obj2);
    intype2 *arg2v = make_array_from_list< intype2 *>(obj2, arg2n);

    llvm_func(arg1, arg2v, arg2n, arg3);
    delete [] arg2v ;

    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype3, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, int, intype3*, unsigned int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj3;
    int arg2;

    if (!PyArg_ParseTuple(args, "OiO", &obj1, &arg2, &obj3))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 >( obj1 );
    const size_t arg3n = PyList_Size(obj3);
    intype3 *arg3v = make_array_from_list< intype3 *>(obj3, arg3n);

    outtype ret = llvm_func(arg1, arg2, arg3v, arg3n);
    delete [] arg3v ;

    return pycap_new<outtype>( ret );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3*, unsigned int),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3;

    if (!PyArg_ParseTuple(args, "OOO", &obj1, &obj2, &obj3))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const size_t arg3n = PyList_Size(obj3);
    intype3 *arg3v = make_array_from_list< intype3 *>(obj3, arg3n);

    outtype ret = llvm_func(arg1, arg2, arg3v, arg3n);
    delete [] arg3v ;

    return pycap_new<outtype>( ret );
    LLVMPY_CATCH_ALL
}

template <class intype1, class intype2, class intype3, class outtype>
PyObject* WF( outtype (&llvm_func)( intype1, intype2, intype3*, unsigned int, const char*),
                     PyObject *self, PyObject *args )
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3;
    const char *arg4;

    if (!PyArg_ParseTuple(args, "OOOs", &obj1, &obj2, &obj3, &arg4))
        return NULL;

    const intype1 arg1 = pycap_get< intype1 > (obj1);
    const intype2 arg2 = pycap_get< intype2 > (obj2);
    const size_t arg3n = PyList_Size(obj3);
    intype3 *arg3v = make_array_from_list< intype3 *>(obj3, arg3n);

    outtype ret = llvm_func(arg1, arg2, arg3v, arg3n, arg4);
    delete [] arg3v ;

    return pycap_new<outtype>( ret );
    LLVMPY_CATCH_ALL
}

/*===----------------------------------------------------------------------===*/
/* Modules                                                                    */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMModuleCreateWithName(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const char *s;

    if (!PyArg_ParseTuple(args, "s:LLVMModuleCreateWithName", &s)) {
        return NULL;
    }

    const LLVMModuleRef module = LLVMModuleCreateWithName(s);
    return pycap_new<LLVMModuleRef>(module);
    LLVMPY_CATCH_ALL
}

MSW(LLVMGetDataLayout, WF<LLVMModuleRef>)
MSW(LLVMSetDataLayout, WF<LLVMModuleRef>)
MSW(LLVMGetModuleIdentifier, WF<LLVMModuleRef>)
MSW(LLVMSetModuleIdentifier, WF<LLVMModuleRef>)
MSW(LLVMGetTarget, WF<LLVMModuleRef>)
MSW(LLVMSetTarget, WF<LLVMModuleRef>)
MSW(LLVMModuleAddLibrary, WF<LLVMModuleRef>)
MSW(LLVMGetTypeByName, (WF<LLVMModuleRef, LLVMTypeRef>))
MSW(LLVMDumpModule, WF<LLVMModuleRef>)
MSW(LLVMDisposeModule, WF<LLVMModuleRef>)
MSW(LLVMDumpModuleToString, WD<LLVMModuleRef>)
MSW( LLVMModuleGetPointerSize, (WF<LLVMModuleRef, unsigned int>))
MSW(LLVMModuleGetOrInsertFunction, (WF<LLVMModuleRef,
                    LLVMTypeRef, LLVMValueRef>))

static PyObject *
_wLLVMVerifyModule(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const LLVMModuleRef m = get_object_arg<LLVMModuleRef>(args) ;
    if (!m) return NULL;

    char *outmsg = 0;
    (void) LLVMVerifyModule(m, LLVMReturnStatusAction, &outmsg);

    PyObject *ret;
    if (outmsg) {
        ret = PyUnicode_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    } else {
        ret = PyUnicode_FromString("");
    }

    return ret;
    LLVMPY_CATCH_ALL
}

///// unused
// typedef LLVMModuleRef (*asm_or_bc_fn_t)(const char *A, unsigned Len, char **OutMessage);


static PyObject*
_wLLVMGetModuleFromAssembly(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const char * str;
    if ( !PyArg_ParseTuple(args, "s", &str) ){
        return NULL;
    }

    char * outmsg = 0;
    const LLVMModuleRef mod = LLVMGetModuleFromAssembly(str, &outmsg);

    if ( !mod ){
        if ( outmsg ){
            PyObject * ret = PyUnicode_FromString(outmsg);
            LLVMDisposeMessage(outmsg);
            return ret;
        } else {
            Py_RETURN_NONE;
        }
    }

    return pycap_new<LLVMModuleRef>(mod);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGetModuleFromBitcode(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj ;

    if (!PyArg_ParseTuple(args, "S", &obj))
        return NULL;

    const char *start = PyBytes_AsString(obj);
    const Py_ssize_t len = PyBytes_Size(obj);

    char *outmsg = 0;
    LLVMModuleRef m = LLVMGetModuleFromBitcode(start, len, &outmsg);

    PyObject *ret;
    if (!m) {
        if (outmsg) {
            ret = PyUnicode_FromString(outmsg);
            LLVMDisposeMessage(outmsg);
            return ret;
        } else {
            Py_RETURN_NONE;
        }
    }

    return pycap_new<LLVMModuleRef>(m);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGetBitcodeFromModule(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const LLVMModuleRef m = get_object_arg<LLVMModuleRef>(args) ;
    if (!m ) return NULL;

    size_t len;
    unsigned const char *ubytes = LLVMGetBitcodeFromModule(m, &len) ;
    if ( !ubytes ) Py_RETURN_NONE;

    const char *chars = reinterpret_cast<const char*>(ubytes) ;
    PyObject *ret = PyBytes_FromStringAndSize(chars, len);
    LLVMDisposeMessage(const_cast<char*>(chars));
    return ret;
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGetNativeCodeFromModule(PyObject * self, PyObject * args)
{
    LLVMPY_TRY
    PyObject * arg_m;
    int arg_use_asm;

    if (!PyArg_ParseTuple(args, "Oi", &arg_m, &arg_use_asm))
        return NULL;

    const LLVMModuleRef m = pycap_get<LLVMModuleRef>( arg_m ) ;

    std::string error;
    size_t len;
    unsigned const char * ubytes
        = LLVMGetNativeCodeFromModule(m, arg_use_asm, &len, error);
    if ( !error.empty() ){
        PyErr_SetString(PyExc_RuntimeError, error.c_str());
    }

    const char *chars = reinterpret_cast<const char*>(ubytes) ;
    PyObject * ret = PyBytes_FromStringAndSize(chars, len);

    LLVMDisposeMessage(const_cast<char*>(chars));

    return ret;
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMLinkModules(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    size_t mode = 0;

    PyObject *dest_obj, *src_obj ;
    if (!PyArg_ParseTuple(args, "OO|I", &dest_obj, &src_obj, &mode))
        return NULL;

    const LLVMModuleRef dest = pycap_get<LLVMModuleRef>(dest_obj ) ;
    const LLVMModuleRef src = pycap_get<LLVMModuleRef>(src_obj) ;

    PyObject *ret;
    char *errmsg;
    if (!LLVMLinkModules(dest, src, (LLVMLinkerMode)mode, &errmsg)) {
        if (errmsg) {
            ret = PyUnicode_FromString(errmsg);
            LLVMDisposeMessage(errmsg);
        } else {
            ret = PyUnicode_FromString("Link error");
        }
        return ret;
    }

    /* note: success => None, failure => string with error message */
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

/*===----------------------------------------------------------------------===*/
/* Types                                                                      */
/*===----------------------------------------------------------------------===*/

/*===-- General ----------------------------------------------------------===*/

MSW(LLVMGetTypeKind, (WF<LLVMTypeRef, LLVMTypeKind>))
MSW(LLVMDumpTypeToString, WD<LLVMTypeRef>)

/*===-- Integer types ----------------------------------------------------===*/

MSW(LLVMInt1Type, WF<LLVMTypeRef>)
MSW(LLVMInt8Type, WF<LLVMTypeRef>)
MSW(LLVMInt16Type, WF<LLVMTypeRef>)
MSW(LLVMInt32Type, WF<LLVMTypeRef>)
MSW(LLVMInt64Type, WF<LLVMTypeRef>)
MSW(LLVMIntType, WF<LLVMTypeRef>)
MSW(LLVMGetIntTypeWidth, (WF<LLVMTypeRef, unsigned int>))

/*===-- Floating-point types ---------------------------------------------===*/

MSW(LLVMFloatType, WF<LLVMTypeRef>)
MSW(LLVMDoubleType, WF<LLVMTypeRef>)
MSW(LLVMX86FP80Type, WF<LLVMTypeRef>)
MSW(LLVMFP128Type, WF<LLVMTypeRef>)
MSW(LLVMPPCFP128Type, WF<LLVMTypeRef>)

/*===-- Function types ---------------------------------------------------===*/

MSW(LLVMFunctionType, (WF<LLVMTypeRef, LLVMTypeRef, LLVMBool, LLVMTypeRef>))
MSW(LLVMIsFunctionVarArg, (WF<LLVMTypeRef, LLVMBool>))
MSW(LLVMGetReturnType, (WF<LLVMTypeRef, LLVMTypeRef>))
MSW(LLVMCountParamTypes, (WF<LLVMTypeRef, unsigned int>))

/* The LLVMGetParamTypes and LLVMGetStructElementTypes functions both
 * have the same signatures. The following implementation takes advantage
 * of this.
 */

typedef void (*obj2arr_fn_t)(LLVMTypeRef ty, LLVMTypeRef *outv);
typedef unsigned (*arrcnt_fn_t)(LLVMTypeRef ty);

static PyObject *
obj2arr(PyObject *self, PyObject *args, arrcnt_fn_t cntfunc, obj2arr_fn_t arrfunc)
{
    size_t param_count;

    /* get the function object ptr */
    const LLVMTypeRef type = get_object_arg<LLVMTypeRef>(args) ;

    /* get param count */
    param_count = cntfunc(type);

    /* alloc enough space for all of them */
    LLVMTypeRef* param_types = new LLVMTypeRef[param_count] ;

    /* call LLVM func */
    arrfunc(type, param_types);

    /* create a list from the array */
    PyObject *list = make_list<LLVMTypeRef>(param_types, param_count);

    /* free temp storage */
    delete [] param_types ;

    return list;
}

static PyObject *
_wLLVMGetFunctionTypeParams(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    return obj2arr(self, args, LLVMCountParamTypes, LLVMGetParamTypes);
    LLVMPY_CATCH_ALL
}

/*===-- Struct types -----------------------------------------------------===*/

MSW(LLVMStructType, (WF<LLVMTypeRef, LLVMTypeRef>))
MSW(LLVMStructTypeIdentified, WF<LLVMTypeRef>)
MSW(LLVMSetStructBody, (WF<LLVMTypeRef, LLVMTypeRef>))
MSW(LLVMCountStructElementTypes, (WF<LLVMTypeRef, unsigned int>))
MSW(LLVMGetStructName, WF<LLVMTypeRef>)
MSW(LLVMSetStructName, WF<LLVMTypeRef>)


static PyObject *
_wLLVMGetStructElementTypes(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    return obj2arr(self, args, LLVMCountStructElementTypes,
            LLVMGetStructElementTypes);
    LLVMPY_CATCH_ALL
}


MSW(LLVMIsPackedStruct, (WF<LLVMTypeRef, LLVMBool>))
MSW(LLVMIsOpaqueStruct, (WF<LLVMTypeRef, LLVMBool>))
MSW(LLVMIsLiteralStruct, (WF<LLVMTypeRef, int>))

/*===-- Array types ------------------------------------------------------===*/

MSW(LLVMArrayType, (WF<LLVMTypeRef, LLVMTypeRef>))
MSW(LLVMGetElementType, (WF<LLVMTypeRef, LLVMTypeRef>))
MSW(LLVMGetArrayLength, (WF<LLVMTypeRef, unsigned int>))

/*===-- Pointer types ----------------------------------------------------===*/

MSW(LLVMPointerType, (WF<LLVMTypeRef, LLVMTypeRef>))
MSW(LLVMGetPointerAddressSpace, (WF<LLVMTypeRef, unsigned int>))

/*===-- Vector type ------------------------------------------------------===*/

MSW(LLVMVectorType, (WF<LLVMTypeRef, LLVMTypeRef>))
MSW(LLVMGetVectorSize, (WF<LLVMTypeRef, unsigned int>))

/*===-- Other types ------------------------------------------------------===*/

MSW(LLVMVoidType, WF<LLVMTypeRef>)
MSW(LLVMLabelType, WF<LLVMTypeRef>)

/*===-- Type handles -----------------------------------------------------===*/

/*
MSW(LLVMCreateTypeHandle, (WF<LLVMTypeRef, LLVMTypeHandleRef>))
MSW(LLVMResolveTypeHandle, (WF<LLVMTypeHandleRef, LLVMTypeRef>))
MSW(LLVMDisposeTypeHandle, WF<LLVMTypeHandleRef>)
*/


/*===----------------------------------------------------------------------===*/
/* Values                                                                     */
/*===----------------------------------------------------------------------===*/

/* Operations on all values */

MSW(LLVMTypeOf, (WF<LLVMValueRef, LLVMTypeRef>))
MSW(LLVMGetValueName, WF<LLVMValueRef>)
MSW(LLVMSetValueName, WF<LLVMValueRef>)
MSW(LLVMDumpValue, WF<LLVMValueRef>)
MSW(LLVMDumpValueToString, WD<LLVMValueRef>)
MSW(LLVMValueGetID, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMValueGetNumUses, (WF<LLVMValueRef, unsigned int>))

static PyObject *
_wLLVMValueGetUses(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const LLVMValueRef value = get_object_arg<LLVMValueRef>(args) ;

    LLVMValueRef *uses = 0;
    size_t n = LLVMValueGetUses(value, &uses);

    PyObject *list = make_list<LLVMValueRef>(uses, n);
    if (n > 0)
        LLVMDisposeValueRefArray(uses);

    return list;
    LLVMPY_CATCH_ALL
}

/*===-- Users ------------------------------------------------------------===*/

MSW(LLVMUserGetNumOperands, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMUserGetOperand,  (WF<LLVMValueRef, LLVMValueRef>))

/*===-- Constant Values --------------------------------------------------===*/

/* Operations on constants of any type */

MSW(LLVMConstNull, (WF<LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstAllOnes, (WF<LLVMTypeRef, LLVMValueRef>))
MSW(LLVMGetUndef, (WF<LLVMTypeRef, LLVMValueRef>))
MSW(LLVMIsConstant, (WF<LLVMValueRef, LLVMBool>))
MSW(LLVMIsNull, (WF<LLVMValueRef, LLVMBool>))
MSW(LLVMIsUndef, (WF<LLVMValueRef, LLVMBool>))

/* Operations on scalar constants */

static PyObject *
_wLLVMConstInt(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj;
    unsigned long long n;
    int sign_extend;

    if (!PyArg_ParseTuple(args, "OKi", &obj, &n, &sign_extend))
        return NULL;

    const LLVMTypeRef ty = pycap_get<LLVMTypeRef>( obj ) ;

    const LLVMValueRef val = LLVMConstInt(ty, n, sign_extend);

    return pycap_new<LLVMValueRef>(val);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMConstReal(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj;
    double d;

    if (!PyArg_ParseTuple(args, "Od", &obj, &d))
        return NULL;

    const LLVMTypeRef ty = pycap_get<LLVMTypeRef>( obj ) ;

    const LLVMValueRef val = LLVMConstReal(ty, d);
    return pycap_new<LLVMValueRef>(val);
    LLVMPY_CATCH_ALL
}

MSW(LLVMConstRealOfString, (WF<LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstIntGetZExtValue, (WF<LLVMValueRef, llvmwrap_ull>))
MSW(LLVMConstIntGetSExtValue, (WF<LLVMValueRef, llvmwrap_ll>))

/* Operations on composite constants */

static PyObject *
_wLLVMConstString(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const char *s;
    int dont_null_terminate;

    if (!PyArg_ParseTuple(args, "si:LLVMConstString", &s, &dont_null_terminate)) {
        return NULL;
    }

    LLVMValueRef val = LLVMConstString(s, strlen(s), dont_null_terminate);
    return pycap_new<LLVMValueRef>(val);
    LLVMPY_CATCH_ALL
}

MSW(LLVMConstArray, (WF<LLVMTypeRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstStruct, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstVector, (WF<LLVMValueRef, LLVMValueRef>))

/* Constant expressions */

MSW(LLVMGetConstExprOpcode, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMGetConstExprOpcodeName, WF<LLVMValueRef>)
MSW(LLVMSizeOf, (WF<LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstNeg, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstNot, (WF<LLVMValueRef, LLVMValueRef>))

MSW(LLVMConstAdd, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstFAdd, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstSub, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstFSub, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstMul, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstFMul, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstUDiv, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstSDiv, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstFDiv, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstURem, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstSRem, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstFRem, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstAnd, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstOr, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstXor, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))

MSW(LLVMConstICmp, (WF_enum1<LLVMIntPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstFCmp, (WF_enum1<LLVMRealPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef>))

MSW(LLVMConstShl, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstLShr, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstAShr, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstGEP, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstTrunc, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstSExt, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstZExt, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstFPTrunc, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstFPExt, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstUIToFP, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstSIToFP, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstFPToUI, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstFPToSI, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstPtrToInt, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstIntToPtr, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstBitCast, (WF<LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMConstSelect, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstExtractElement, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstInsertElement, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMConstShuffleVector, (WF<LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))


/*===----------------------------------------------------------------------===*/
/* Globals                                                                    */
/*===----------------------------------------------------------------------===*/

/*===-- Globals ----------------------------------------------------------===*/

MSW(LLVMGetGlobalParent, (WF<LLVMValueRef, LLVMModuleRef>))
MSW(LLVMIsDeclaration, (WF<LLVMValueRef, LLVMBool>))
MSW(LLVMGetLinkage, (WF<LLVMValueRef, LLVMLinkage>))
MSW(LLVMSetLinkage, (WF_enum2<LLVMValueRef, LLVMLinkage>))
MSW(LLVMGetSection, WF<LLVMValueRef>)
MSW(LLVMSetSection, WF<LLVMValueRef>)
MSW(LLVMGetVisibility, (WF<LLVMValueRef, LLVMVisibility>))
MSW(LLVMSetVisibility, (WF_enum2<LLVMValueRef, LLVMVisibility>))
MSW(LLVMGetAlignment, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMSetAlignment, WF_int2<LLVMValueRef>)

/*===-- Global Variables -------------------------------------------------===*/

MSW(LLVMAddGlobal, (WF<LLVMModuleRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMGetNamedGlobal, (WF<LLVMModuleRef, LLVMValueRef>))
MSW(LLVMGetFirstGlobal, (WF<LLVMModuleRef, LLVMValueRef>))
MSW(LLVMGetNextGlobal, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMDeleteGlobal, WF<LLVMValueRef>)
MSW(LLVMHasInitializer, (WF<LLVMValueRef, int >))
MSW(LLVMGetInitializer, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMSetInitializer, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMSetGlobalConstant, WF_int2<LLVMValueRef>)
MSW(LLVMIsGlobalConstant, (WF<LLVMValueRef, LLVMBool>))
MSW(LLVMSetThreadLocal, WF_int2<LLVMValueRef>)
MSW(LLVMIsThreadLocal, (WF<LLVMValueRef, LLVMBool>))


/*===-- Functions --------------------------------------------------------===*/

MSW(LLVMAddFunction, (WF<LLVMModuleRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMGetNamedFunction, (WF<LLVMModuleRef, LLVMValueRef>))
MSW(LLVMGetFirstFunction, (WF<LLVMModuleRef, LLVMValueRef>))
MSW(LLVMGetNextFunction, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMDeleteFunction, WF<LLVMValueRef>)
MSW(LLVMGetIntrinsicID, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMGetFunctionCallConv, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMSetFunctionCallConv, WF_int2<LLVMValueRef>)
MSW(LLVMGetGC, WF<LLVMValueRef>)
MSW(LLVMSetGC, WF<LLVMValueRef>)
MSW(LLVMGetDoesNotThrow, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMSetDoesNotThrow, WF_int2<LLVMValueRef>)
MSW(LLVMViewFunctionCFG, WF<LLVMValueRef>)
MSW(LLVMViewFunctionCFGOnly, WF<LLVMValueRef>)
MSW(LLVMAddFunctionAttr, (WF_enum2<LLVMValueRef, LLVMAttribute>))
MSW(LLVMRemoveFunctionAttr, (WF_enum2<LLVMValueRef, LLVMAttribute>))


static PyObject *
_wLLVMVerifyFunction(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const LLVMValueRef fn = get_object_arg<LLVMValueRef>(args);
    if (!fn) return NULL;

    return pycap_new<int>(LLVMVerifyFunction(fn, LLVMReturnStatusAction));
    LLVMPY_CATCH_ALL
}


/*===-- Arguments --------------------------------------------------------===*/

MSW(LLVMCountParams, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMGetFirstParam, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMGetNextParam, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMGetParamParent, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMAddAttribute, (WF_enum2<LLVMValueRef, LLVMAttribute>))
MSW(LLVMRemoveAttribute, (WF_enum2<LLVMValueRef, LLVMAttribute>))
MSW(LLVMSetParamAlignment, (WF_enum2<LLVMValueRef, unsigned int>))
MSW(LLVMGetParamAlignment, (WF<LLVMValueRef, unsigned int>))

/*===-- Basic Blocks -----------------------------------------------------===*/

MSW(LLVMGetBasicBlockParent, (WF<LLVMBasicBlockRef, LLVMValueRef>))
MSW(LLVMCountBasicBlocks, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMGetFirstBasicBlock, (WF<LLVMValueRef, LLVMBasicBlockRef>))
MSW(LLVMGetNextBasicBlock, (WF<LLVMBasicBlockRef, LLVMBasicBlockRef>))
MSW(LLVMGetEntryBasicBlock, (WF<LLVMValueRef, LLVMBasicBlockRef>))
MSW(LLVMAppendBasicBlock, (WF<LLVMValueRef, LLVMBasicBlockRef>))
MSW(LLVMInsertBasicBlock, (WF<LLVMBasicBlockRef, LLVMBasicBlockRef>))
MSW(LLVMDeleteBasicBlock, WF<LLVMBasicBlockRef>)

/*===-- MetaData -----------------------------------------------------===*/

MSW(LLVMMetaDataGet, (WF<LLVMModuleRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMAddNamedMetadataOperand, (WF<LLVMModuleRef, LLVMValueRef>))
MSW(LLVMMetaDataGetOperand, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMMetaDataGetNumOperands, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMMetaDataStringGet, (WF<LLVMModuleRef, LLVMValueRef>))

static PyObject *
_wLLVMGetNamedMetadataOperands(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj_module;
    const char *name;

    if (!PyArg_ParseTuple(args, "Os", &obj_module, &name))
        return NULL;

    LLVMModuleRef module = pycap_get<LLVMModuleRef>(obj_module);
    unsigned num_operands = LLVMGetNamedMetadataNumOperands(module, name);
    LLVMValueRef *operands = new LLVMValueRef[num_operands];
    LLVMGetNamedMetadataOperands(module, name, operands);

    PyObject *list = make_list<LLVMValueRef>(operands, num_operands);
    delete [] operands;

    return list;
    LLVMPY_CATCH_ALL
}

/*===-- Instructions -----------------------------------------------------===*/

MSW(LLVMGetInstructionParent, (WF<LLVMValueRef, LLVMBasicBlockRef>))
MSW(LLVMGetFirstInstruction, (WF<LLVMBasicBlockRef, LLVMValueRef>))
MSW(LLVMGetNextInstruction, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMInstIsTerminator,   (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsBinaryOp,     (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsShift,        (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsCast,         (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsLogicalShift, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsArithmeticShift, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsAssociative,  (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsCommutative,  (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstIsVolatile,     (WF<LLVMValueRef, unsigned int>))
MSW(LLVMSetVolatile,    WF_int2<LLVMValueRef>)
MSW(LLVMInstGetOpcode,      (WF<LLVMValueRef, unsigned int>))
MSW(LLVMInstGetOpcodeName,  WF<LLVMValueRef>)

MSW(LLVMInstSetMetaData, (WF<LLVMValueRef, LLVMValueRef>))

/*===-- Call Sites (Call or Invoke) --------------------------------------===*/

MSW(LLVMSetInstructionCallConv, WF_int2<LLVMValueRef>)
MSW(LLVMGetInstructionCallConv, (WF<LLVMValueRef, unsigned int>))
MSW(LLVMAddInstrAttribute, (WF<LLVMValueRef, LLVMAttribute>))
MSW(LLVMRemoveInstrAttribute, (WF<LLVMValueRef, LLVMAttribute>))
MSW(LLVMSetInstrParamAlignment, WF<LLVMValueRef>)
MSW(LLVMIsTailCall, (WF<LLVMValueRef, LLVMBool>))
MSW(LLVMSetTailCall, WF_int2<LLVMValueRef>)
MSW(LLVMInstGetCalledFunction, (WF<LLVMValueRef, LLVMValueRef>))

/*===-- PHI Nodes --------------------------------------------------------===*/

static void LLVMAddIncoming1(LLVMValueRef PhiNode, LLVMValueRef IncomingValue, LLVMBasicBlockRef IncomingBlock)
{
    LLVMAddIncoming(PhiNode, &IncomingValue, &IncomingBlock, 1);
}

MSW(LLVMAddIncoming1, (WF<LLVMValueRef, LLVMValueRef, LLVMBasicBlockRef>))
MSW(LLVMCountIncoming,       (WF<LLVMValueRef, unsigned int>))
MSW(LLVMGetIncomingValue, (WF<LLVMValueRef, LLVMValueRef>))
MSW(LLVMGetIncomingBlock, (WF<LLVMValueRef, LLVMBasicBlockRef>))

/*===-- Compare Instructions ---------------------------------------------===*/

MSW(LLVMCmpInstGetPredicate, (WF<LLVMValueRef, unsigned int>))

/*===-- Instruction builders ----------------------------------------------===*/

MSW(LLVMCreateBuilder, WF<LLVMBuilderRef>)
MSW(LLVMPositionBuilderBefore, (WF<LLVMBuilderRef, LLVMValueRef>))
MSW(LLVMPositionBuilderAtEnd, (WF<LLVMBuilderRef, LLVMBasicBlockRef>))
MSW(LLVMGetInsertBlock, (WF<LLVMBuilderRef, LLVMBasicBlockRef>))
MSW(LLVMDisposeBuilder, WF<LLVMBuilderRef>)

/* Terminators */

MSW(LLVMBuildRetVoid, (WF<LLVMBuilderRef, LLVMValueRef>))
MSW(LLVMBuildRet, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildRetMultiple, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildBr, (WF<LLVMBuilderRef, LLVMBasicBlockRef, LLVMValueRef>))
MSW(LLVMBuildCondBr, (WF<LLVMBuilderRef, LLVMValueRef, LLVMBasicBlockRef, LLVMBasicBlockRef, LLVMValueRef>))
MSW(LLVMBuildSwitch, (WF<LLVMBuilderRef, LLVMValueRef, LLVMBasicBlockRef, LLVMValueRef>))

static PyObject *
_wLLVMBuildInvoke(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj1, *obj2, *obj3, *obj4, *obj5;
    const char *name;

    if (!PyArg_ParseTuple(args, "OOOOOs:LLVMBuildInvoke", &obj1, &obj2, &obj3, &obj4, &obj5, &name)) {
        return NULL;
    }

    const LLVMBuilderRef builder = pycap_get<LLVMBuilderRef>( obj1);
    const LLVMValueRef func = pycap_get<LLVMValueRef>( obj2 ) ;

    size_t fnarg_count = PyList_Size(obj3);
    LLVMValueRef *fnargs
        = make_array_from_list<LLVMValueRef *>(obj3, fnarg_count);

    const LLVMBasicBlockRef then_blk = pycap_get<LLVMBasicBlockRef> ( obj4 ) ;
    const LLVMBasicBlockRef catch_blk = pycap_get<LLVMBasicBlockRef> ( obj5 ) ;

    const LLVMValueRef inst
        = LLVMBuildInvoke(builder, func, fnargs, fnarg_count, then_blk,
                catch_blk, name);

    delete [] fnargs;

    return pycap_new<LLVMValueRef>(inst);
    LLVMPY_CATCH_ALL
}

MSW(LLVMBuildUnreachable, (WF<LLVMBuilderRef, LLVMValueRef>))

/* Add a case to the switch instruction */

MSW(LLVMAddCase, (WF<LLVMValueRef, LLVMValueRef, LLVMBasicBlockRef>))

/* Arithmetic */

MSW(LLVMBuildAdd, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFAdd, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildSub, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFSub, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildMul, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFMul, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildUDiv, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildSDiv, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFDiv, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildURem, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildSRem, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFRem, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildShl, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildLShr, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildAShr, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildAnd, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildOr, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildXor, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildNeg, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildNot, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))

/* Memory */

MSW(LLVMBuildMalloc, (WF<LLVMBuilderRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildArrayMalloc, (WF<LLVMBuilderRef, LLVMTypeRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildAlloca, (WF<LLVMBuilderRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildArrayAlloca, (WF<LLVMBuilderRef, LLVMTypeRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFree, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildLoad, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildStore, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildGEP, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))

MSW(LLVMLdSetAlignment, WF_int2<LLVMValueRef>)
MSW(LLVMStSetAlignment, WF_int2<LLVMValueRef>)

/* Casts */

MSW(LLVMBuildTrunc, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildZExt, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildSExt, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildFPToUI, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildFPToSI, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildUIToFP, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildSIToFP, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildFPTrunc, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildFPExt, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildPtrToInt, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildIntToPtr, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildBitCast, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))

/* Comparisons */

MSW(LLVMBuildICmp, (WF_enum2_char4<LLVMBuilderRef, LLVMIntPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFCmp, (WF_enum2_char4<LLVMBuilderRef, LLVMRealPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef>))


/* Atomics */
MSW(LLVMBuildAtomicCmpXchg, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildAtomicRMW, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildAtomicLoad, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildAtomicStore, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildFence, (WF<LLVMBuilderRef, LLVMValueRef>))

/* Miscellaneous instructions */

MSW(LLVMBuildGetResult, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildInsertValue, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildPhi, (WF<LLVMBuilderRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildCall, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildSelect, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildVAArg, (WF<LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef>))
MSW(LLVMBuildExtractElement, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildInsertElement, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))
MSW(LLVMBuildShuffleVector, (WF<LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef>))


/*===----------------------------------------------------------------------===*/
/* Memory Buffer                                                              */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMCreateMemoryBufferWithContentsOfFile(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const char *path;
    LLVMMemoryBufferRef ref;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s:LLVMCreateMemoryBufferWithContentsOfFile", &path)) {
        return NULL;
    }

    char *outmsg;
    if (!LLVMCreateMemoryBufferWithContentsOfFile(path, &ref, &outmsg)) {
        ret = pycap_new<LLVMMemoryBufferRef>(ref);
    } else {
        ret = PyUnicode_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    }

    return ret;
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMCreateMemoryBufferWithSTDIN(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *ret;
    LLVMMemoryBufferRef ref;
    char *outmsg;
    if (!LLVMCreateMemoryBufferWithSTDIN(&ref, &outmsg)) {
        ret = pycap_new<LLVMMemoryBufferRef>(ref);
    } else {
        ret = PyUnicode_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    }

    return ret;
    LLVMPY_CATCH_ALL
}

MSW(LLVMDisposeMemoryBuffer, WF<LLVMMemoryBufferRef>)


/*===----------------------------------------------------------------------===*/
/* Pass Manager Builder                                                       */
/*===----------------------------------------------------------------------===*/

MSW(LLVMPassManagerBuilderCreate, WF<LLVMPassManagerBuilderRef>)
MSW(LLVMPassManagerBuilderDispose, WF<LLVMPassManagerBuilderRef>)

MSW(LLVMPassManagerBuilderSetOptLevel, WF_int2<LLVMPassManagerBuilderRef>)
MSW(LLVMPassManagerBuilderGetOptLevel, (WF<LLVMPassManagerBuilderRef, int>))

MSW(LLVMPassManagerBuilderSetSizeLevel, WF_int2<LLVMPassManagerBuilderRef>)
MSW(LLVMPassManagerBuilderGetSizeLevel, (WF<LLVMPassManagerBuilderRef, int>))

MSW(LLVMPassManagerBuilderSetVectorize, WF_int2<LLVMPassManagerBuilderRef>)
MSW(LLVMPassManagerBuilderGetVectorize, (WF<LLVMPassManagerBuilderRef, int>))

MSW(LLVMPassManagerBuilderSetDisableUnitAtATime,
                  WF_int2<LLVMPassManagerBuilderRef>)
MSW(LLVMPassManagerBuilderGetDisableUnitAtATime,
              (WF<LLVMPassManagerBuilderRef, int>))

MSW(LLVMPassManagerBuilderSetDisableUnrollLoops,
                  WF_int2<LLVMPassManagerBuilderRef>)
MSW(LLVMPassManagerBuilderGetDisableUnrollLoops,
              (WF<LLVMPassManagerBuilderRef, int>))

MSW(LLVMPassManagerBuilderSetDisableSimplifyLibCalls,
                  WF_int2<LLVMPassManagerBuilderRef>)
MSW(LLVMPassManagerBuilderGetDisableSimplifyLibCalls,
              (WF<LLVMPassManagerBuilderRef, int>))

MSW(LLVMPassManagerBuilderUseInlinerWithThreshold,
                  WF_int2<LLVMPassManagerBuilderRef>)


MSW(LLVMPassManagerBuilderPopulateFunctionPassManager,
                  (WF<LLVMPassManagerBuilderRef,
                  LLVMPassManagerRef>))

MSW(LLVMPassManagerBuilderPopulateModulePassManager,
                  (WF<LLVMPassManagerBuilderRef,
                  LLVMPassManagerRef>))


/*===----------------------------------------------------------------------===*/
/* Pass Manager                                                               */
/*===----------------------------------------------------------------------===*/

MSW(LLVMCreatePassManager, WF<LLVMPassManagerRef>)
MSW(LLVMCreateFunctionPassManagerForModule, (WF<LLVMModuleRef, LLVMPassManagerRef>))
MSW(LLVMRunPassManager, (WF<LLVMPassManagerRef, LLVMModuleRef, int>))
MSW(LLVMInitializeFunctionPassManager, (WF<LLVMPassManagerRef, int>))
MSW(LLVMRunFunctionPassManager, (WF<LLVMPassManagerRef, LLVMValueRef, int>))
MSW(LLVMFinalizeFunctionPassManager, (WF<LLVMPassManagerRef, int>))
MSW(LLVMDisposePassManager, WF<LLVMPassManagerRef>)
MW(LLVMDumpPasses)
MSW(LLVMAddPassByName, (WF<LLVMPassManagerRef, int>))


MW(LLVMInitializePasses)

MSW(LLVMInitializeNativeTarget, WF<int>)
MSW(LLVMInitializeNativeTargetAsmPrinter, WF<int>)
#if !defined(LLVM_DISABLE_PTX)
# if LLVM_HAS_NVPTX
MW(LLVMInitializeNVPTXTarget)
MW(LLVMInitializeNVPTXTargetInfo)
MW( LLVMInitializeNVPTXTargetMC )
MW(LLVMInitializeNVPTXAsmPrinter)
# else
MW(LLVMInitializePTXTarget)
MW(LLVMInitializePTXTargetInfo)
MW( LLVMInitializePTXTargetMC )
MW(LLVMInitializePTXAsmPrinter)
# endif
#endif

/*===----------------------------------------------------------------------===*/
/* Passes                                                                     */
/*===----------------------------------------------------------------------===*/
/*

#define _wrap_pass(P)   \
MSW( LLVMAdd ## P ## Pass, WF<LLVMPassManagerRef>)

_wrap_pass( AAEval )
_wrap_pass( AggressiveDCE )
_wrap_pass( AliasAnalysisCounter )
_wrap_pass( AlwaysInliner )
_wrap_pass( ArgumentPromotion )
_wrap_pass( BasicAliasAnalysis )
_wrap_pass( BlockPlacement )
_wrap_pass( BreakCriticalEdges )
_wrap_pass( CFGSimplification )
_wrap_pass( CodeGenPrepare )
_wrap_pass( ConstantMerge )
_wrap_pass( ConstantPropagation )
_wrap_pass( DbgInfoPrinter )
_wrap_pass( DeadArgElimination )
_wrap_pass( DeadCodeElimination )
_wrap_pass( DeadInstElimination )
_wrap_pass( DeadStoreElimination )
_wrap_pass( DemoteRegisterToMemory )
_wrap_pass( DomOnlyPrinter )
_wrap_pass( DomOnlyViewer )
_wrap_pass( DomPrinter )
_wrap_pass( DomViewer )
_wrap_pass( EdgeProfiler )
_wrap_pass( FunctionAttrs )
_wrap_pass( FunctionInlining )
//_wrap_pass( GEPSplitter )
_wrap_pass( GlobalDCE )
_wrap_pass( GlobalOptimizer )
_wrap_pass( GlobalsModRef )
_wrap_pass( GVN )
_wrap_pass( IndVarSimplify )
_wrap_pass( InstCount )
_wrap_pass( InstructionCombining )
_wrap_pass( InstructionNamer )
_wrap_pass( IPConstantPropagation )
_wrap_pass( IPSCCP )
_wrap_pass( JumpThreading )
_wrap_pass( LazyValueInfo )
_wrap_pass( LCSSA )
_wrap_pass( LICM )
//_wrap_pass( LiveValues )
_wrap_pass( LoopDeletion )
_wrap_pass( LoopDependenceAnalysis )
_wrap_pass( LoopExtractor )
//_wrap_pass( LoopIndexSplit )
_wrap_pass( LoopRotate )
_wrap_pass( LoopSimplify )
_wrap_pass( LoopStrengthReduce )
_wrap_pass( LoopUnroll )
_wrap_pass( LoopUnswitch )
_wrap_pass( LowerInvoke )
_wrap_pass( LowerSwitch )
_wrap_pass( MemCpyOpt )
_wrap_pass( MergeFunctions )
_wrap_pass( NoAA )
_wrap_pass( NoProfileInfo )
_wrap_pass( OptimalEdgeProfiler )
_wrap_pass( PartialInlining )
//_wrap_pass( PartialSpecialization )
_wrap_pass( PostDomOnlyPrinter )
_wrap_pass( PostDomOnlyViewer )
_wrap_pass( PostDomPrinter )
_wrap_pass( PostDomViewer )
_wrap_pass( ProfileEstimator )
_wrap_pass( ProfileLoader )
_wrap_pass( ProfileVerifier )
_wrap_pass( PromoteMemoryToRegister )
_wrap_pass( PruneEH )
_wrap_pass( Reassociate )
_wrap_pass( ScalarEvolutionAliasAnalysis )
_wrap_pass( ScalarReplAggregates )
_wrap_pass( SCCP )
//_wrap_pass( SimplifyHalfPowrLibCalls )
_wrap_pass( SimplifyLibCalls )
_wrap_pass( SingleLoopExtractor )
_wrap_pass( StripDeadPrototypes )
_wrap_pass( StripNonDebugSymbols )
_wrap_pass( StripSymbols )
//_wrap_pass( StructRetPromotion )
_wrap_pass( TailCallElimination )
//_wrap_pass( TailDuplication )
_wrap_pass( UnifyFunctionExitNodes )

_wrap_pass( Internalize2 )
*/


/*===----------------------------------------------------------------------===*/
/* Target Machine                                                             */
/*===----------------------------------------------------------------------===*/

MW(LLVMGetHostCPUName);

MSW(LLVMTargetMachineFromEngineBuilder, (WF<LLVMEngineBuilderRef,
              LLVMTargetMachineRef>))
MSW(LLVMDisposeTargetMachine, WF<LLVMTargetMachineRef>)

static PyObject *
_wLLVMTargetMachineLookup(PyObject * self, PyObject * args)
{
    LLVMPY_TRY
    const char *arch;
    const char *cpu;
    const char *features;
    int opt;

    if (!PyArg_ParseTuple(args, "sssi", &arch, &cpu, &features, &opt))
        return NULL;

    std::string error;
    LLVMTargetMachineRef tm = LLVMTargetMachineLookup(arch, cpu, features, opt,
                                                      error);
    if(!error.empty()){
        PyErr_SetString(PyExc_RuntimeError, error.c_str());
        return NULL;
    }
    return pycap_new<LLVMTargetMachineRef>(tm);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMTargetMachineEmitFile(PyObject * self, PyObject * args)
{
    LLVMPY_TRY
    PyObject *arg_tm, *arg_m;
    int arg_use_asm;

    if (!PyArg_ParseTuple(args, "OOi", &arg_tm, &arg_m, &arg_use_asm))
        return NULL;

    const LLVMTargetMachineRef tm
        = pycap_get<LLVMTargetMachineRef>( arg_tm ) ;
    const LLVMModuleRef m = pycap_get<LLVMModuleRef>( arg_m ) ;

    std::string error;
    size_t len;
    unsigned const char * ubytes
        = LLVMTargetMachineEmitFile(tm, m, arg_use_asm, &len, error);
    if ( !error.empty() ){
        PyErr_SetString(PyExc_RuntimeError, error.c_str());
        return NULL;
    }

    const char *chars = reinterpret_cast<const char*>(ubytes) ;
    PyObject * ret = PyBytes_FromStringAndSize(chars, len);
    delete [] ubytes;
    return ret;
    LLVMPY_CATCH_ALL
}

MSW(LLVMTargetMachineGetTargetData, (WF<LLVMTargetMachineRef,
              LLVMTargetDataRef>))
MSW(LLVMTargetMachineGetTargetName, WF<LLVMTargetMachineRef>)
MSW(LLVMTargetMachineGetTargetShortDescription, WF<LLVMTargetMachineRef>)
MSW(LLVMTargetMachineGetTriple, WF<LLVMTargetMachineRef>)
MSW(LLVMTargetMachineGetCPU, WF<LLVMTargetMachineRef>)
MSW(LLVMTargetMachineGetFS, WF<LLVMTargetMachineRef>)
MW(LLVMPrintRegisteredTargetsForVersion)


/*===----------------------------------------------------------------------===*/
/* Target Data                                                                */
/*===----------------------------------------------------------------------===*/

MSW(LLVMCreateTargetData, WF<LLVMTargetDataRef>)
MSW(LLVMDisposeTargetData, WF<LLVMTargetDataRef>)

static PyObject *
_wLLVMTargetDataAsString(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const LLVMTargetDataRef td = get_object_arg<LLVMTargetDataRef>(args);

    char *tdrep = LLVMCopyStringRepOfTargetData(td);
    PyObject *ret = PyUnicode_FromString(tdrep);
    LLVMDisposeMessage(tdrep);
    return ret;
    LLVMPY_CATCH_ALL
}

MSW(LLVMAddTargetData, (WF<LLVMTargetDataRef, LLVMPassManagerRef>))
MSW(LLVMByteOrder, (WF<LLVMTargetDataRef, LLVMByteOrdering>))
MSW(LLVMPointerSize, (WF<LLVMTargetDataRef, unsigned int>))
MSW(LLVMIntPtrType, (WF<LLVMTargetDataRef, LLVMTypeRef>))
MSW(LLVMSizeOfTypeInBits, (WF<LLVMTargetDataRef, LLVMTypeRef, llvmwrap_ull>))
MSW(LLVMStoreSizeOfType, (WF<LLVMTargetDataRef, LLVMTypeRef, llvmwrap_ull>))
MSW(LLVMABISizeOfType, (WF<LLVMTargetDataRef, LLVMTypeRef, llvmwrap_ull>))
MSW(LLVMABIAlignmentOfType, (WF<LLVMTargetDataRef, LLVMTypeRef, unsigned int>))
MSW(LLVMCallFrameAlignmentOfType, (WF<LLVMTargetDataRef, LLVMTypeRef, unsigned int>))
MSW(LLVMPreferredAlignmentOfType, (WF<LLVMTargetDataRef, LLVMTypeRef, unsigned int>))
MSW(LLVMPreferredAlignmentOfGlobal, (WF<LLVMTargetDataRef, LLVMValueRef, unsigned int>))
MSW(LLVMElementAtOffset, (WF<LLVMTargetDataRef, LLVMTypeRef, unsigned int>))
MSW(LLVMOffsetOfElement, (WF<LLVMTargetDataRef, LLVMTypeRef,
        llvmwrap_ull>))


/*===----------------------------------------------------------------------===*/
/* Engine Builder                                                             */
/*===----------------------------------------------------------------------===*/

MSW(LLVMCreateEngineBuilder, (WF<LLVMModuleRef, LLVMEngineBuilderRef>))
MSW(LLVMDisposeEngineBuilder, WF<LLVMEngineBuilderRef>)
MSW(LLVMEngineBuilderForceJIT, WF<LLVMEngineBuilderRef>)
MSW(LLVMEngineBuilderForceInterpreter, WF<LLVMEngineBuilderRef>)
MSW(LLVMEngineBuilderSetOptLevel, WF_int2<LLVMEngineBuilderRef>)
MSW(LLVMEngineBuilderSetMCPU, WF<LLVMEngineBuilderRef>)
MSW(LLVMEngineBuilderSetMAttrs, WF<LLVMEngineBuilderRef>)

static PyObject *
_wLLVMEngineBuilderCreate(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const LLVMEngineBuilderRef obj
        = get_object_arg<LLVMEngineBuilderRef>(args) ;

    std::string outmsg;
    const LLVMExecutionEngineRef ee = LLVMEngineBuilderCreate(obj, outmsg);

    PyObject * ret;
    if( !ee ){ // check if error message is set.
        ret = PyUnicode_FromString(outmsg.c_str());
    }else{
        ret = pycap_new<LLVMExecutionEngineRef>(ee);
    }

    return ret;
    LLVMPY_CATCH_ALL
}

/*===----------------------------------------------------------------------===*/
/* Execution Engine                                                           */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMCreateExecutionEngine(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj;
    int force_interpreter;
    char *outmsg = 0;
    int error;

    if (!PyArg_ParseTuple(args, "Oi", &obj, &force_interpreter))
        return NULL;

    const LLVMModuleRef mod = pycap_get<LLVMModuleRef>( obj ) ;

    LLVMExecutionEngineRef ee;
    if (force_interpreter)
        error = LLVMCreateInterpreterForModule(&ee, mod, &outmsg);
    else
        error = LLVMCreateJITCompilerForModule(&ee, mod, 1 /*fast*/, &outmsg);

    PyObject *ret;
    if (error) {
        ret = PyUnicode_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    } else {
        ret = pycap_new<LLVMExecutionEngineRef>(ee);
    }

    return ret;
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGetPointerToFunction(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj_ee;
    PyObject *obj_fn;

    if (!PyArg_ParseTuple(args, "OO", &obj_ee, &obj_fn))
        return NULL;

    const LLVMExecutionEngineRef ee = pycap_get<LLVMExecutionEngineRef>(obj_ee ) ;
    const LLVMValueRef fn = pycap_get<LLVMValueRef>( obj_fn ) ;

    return PyLong_FromVoidPtr(LLVMGetPointerToFunction(ee,fn));
    LLVMPY_CATCH_ALL
}

/* the args should have been ptr, num */
LLVMGenericValueRef LLVMRunFunction2(LLVMExecutionEngineRef EE,
    LLVMValueRef F, LLVMGenericValueRef *Args, unsigned NumArgs)
{
    return LLVMRunFunction(EE, F, NumArgs, Args);
}

static PyObject *
_wLLVMRemoveModule2(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj_ee;
    PyObject *obj_mod;
    if (!PyArg_ParseTuple(args, "OO", &obj_ee, &obj_mod))
        return NULL;

    const LLVMExecutionEngineRef ee = pycap_get<LLVMExecutionEngineRef>( obj_ee ) ;
    const LLVMModuleRef mod = pycap_get<LLVMModuleRef>(obj_mod) ;

    char *outmsg = 0;
    LLVMModuleRef mod_new = 0;
    LLVMRemoveModule(ee, mod, &mod_new, &outmsg);
    PyObject *ret;
    if (mod_new) {
        ret = pycap_new<LLVMModuleRef>(mod_new);
    } else {
        if (outmsg) {
            ret = PyUnicode_FromString(outmsg);
            LLVMDisposeMessage(outmsg);
        } else {
            ret = PyUnicode_FromString("error");
        }
    }

    return ret;
    LLVMPY_CATCH_ALL
}

MSW(LLVMDisposeExecutionEngine, WF<LLVMExecutionEngineRef>)
MSW(LLVMRunFunction2, (WF<LLVMExecutionEngineRef,
    LLVMValueRef, LLVMGenericValueRef, LLVMGenericValueRef>))
MSW(LLVMGetExecutionEngineTargetData, (WF<LLVMExecutionEngineRef,
    LLVMTargetDataRef>))
MSW(LLVMRunStaticConstructors, WF<LLVMExecutionEngineRef>)
MSW(LLVMRunStaticDestructors, WF<LLVMExecutionEngineRef>)
MSW(LLVMFreeMachineCodeForFunction, (WF<LLVMExecutionEngineRef, LLVMValueRef>))
MSW(LLVMAddModule, (WF<LLVMExecutionEngineRef, LLVMModuleRef>))


/*===----------------------------------------------------------------------===*/
/* Generic Value                                                              */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMCreateGenericValueOfInt(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj1;
    unsigned long long n;
    int is_signed;
    LLVMGenericValueRef gv;

    if (!PyArg_ParseTuple(args, "OLi", &obj1, &n, &is_signed))
        return NULL;

    const LLVMTypeRef ty = pycap_get<LLVMTypeRef>( obj1 ) ;

    gv = LLVMCreateGenericValueOfInt(ty, n, is_signed);
    return pycap_new<LLVMGenericValueRef>(gv);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMCreateGenericValueOfFloat(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj1;
    double d;
    LLVMGenericValueRef gv;

    if (!PyArg_ParseTuple(args, "Od", &obj1, &d))
        return NULL;

    const LLVMTypeRef ty = pycap_get<LLVMTypeRef>( obj1 ) ;

    gv = LLVMCreateGenericValueOfFloat(ty, d);
    return pycap_new<LLVMGenericValueRef>(gv);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMCreateGenericValueOfPointer(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
//    PyObject *obj1;
//    LLVMTypeRef ty; //unused?
    unsigned long long n_;
    size_t n;

    if (!PyArg_ParseTuple(args, "L", &n_))
        return NULL;

    n=n_;

    const LLVMGenericValueRef gv = LLVMCreateGenericValueOfPointer((void*)n);
    return pycap_new<LLVMGenericValueRef>(gv);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGenericValueToInt(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj1;
    int is_signed;
    unsigned long long val;

    if (!PyArg_ParseTuple(args, "Oi", &obj1, &is_signed))
        return NULL;

    LLVMGenericValueRef gv = pycap_get<LLVMGenericValueRef>(obj1);

    val = LLVMGenericValueToInt(gv, is_signed);
    return is_signed ?
        PyLong_FromLongLong((long long)val) :
        PyLong_FromUnsignedLongLong(val);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGenericValueToFloat(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj1, *obj2;

    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))
        return NULL;

    const LLVMTypeRef ty = pycap_get<LLVMTypeRef>( obj1 ) ;
    const LLVMGenericValueRef gv = pycap_get<LLVMGenericValueRef>( obj2 ) ;

    double val = LLVMGenericValueToFloat(ty, gv);
    return PyFloat_FromDouble(val);
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGenericValueToPointer(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj1;

    if (!PyArg_ParseTuple(args, "O", &obj1))
        return NULL;

    const LLVMGenericValueRef gv = pycap_get<LLVMGenericValueRef>( obj1 ) ;

    void * val = LLVMGenericValueToPointer(gv);
    return PyLong_FromVoidPtr(val);
    LLVMPY_CATCH_ALL
}

MSW(LLVMDisposeGenericValue, WF<LLVMGenericValueRef>)


/*===----------------------------------------------------------------------===*/
/* Misc                                                                       */
/*===----------------------------------------------------------------------===*/

MSW(LLVMGetIntrinsic, (WF<LLVMModuleRef, LLVMTypeRef, LLVMValueRef>))

static PyObject *
_wLLVMLoadLibraryPermanently(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const char *filename;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s:LLVMLoadLibraryPermanently", &filename)) {
        return NULL;
    }

    char *outmsg = 0;
    if (!LLVMLoadLibraryPermanently(filename, &outmsg)) {
        if (outmsg) {
            ret = PyUnicode_FromString(outmsg);
            LLVMDisposeMessage(outmsg);
            return ret;
        }
    }

    /* note: success => None, failure => string with error message */
    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMParseEnvOpts(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const char * progname;
    const char * envname;
    if(!PyArg_ParseTuple(args, "ss", &progname, &envname)) {
        return NULL;
    }

    llvm::cl::ParseEnvironmentOptions(progname, envname);

    Py_RETURN_NONE;
    LLVMPY_CATCH_ALL
}

MSW(LLVMInlineFunction, (WF<LLVMValueRef, int>))

/* Expose the void* inside a PyCObject as a PyLong. This allows us to
 * use it as a unique ID. */
static PyObject *
_wPyCObjectVoidPtrToPyLong(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    void *p = get_object_arg(args);
    return PyLong_FromVoidPtr(p);
    LLVMPY_CATCH_ALL
}

/*===----------------------------------------------------------------------===*/
/* Python member method table                                                 */
/*===----------------------------------------------------------------------===*/

#define _method( func ) \
{ # func , static_cast< PyCFunction > ( _w ## func ) , METH_VARARGS , NULL },
#define _pass( P )         _method( LLVMAdd ## P ## Pass )

static PyMethodDef core_methods[] = {

    /* Modules */
    _method( LLVMModuleCreateWithName )
    _method( LLVMGetDataLayout )
    _method( LLVMSetDataLayout )
    _method( LLVMGetModuleIdentifier )
    _method( LLVMSetModuleIdentifier )
    _method( LLVMGetTarget )
    _method( LLVMSetTarget )
    _method( LLVMModuleAddLibrary )
    _method( LLVMGetTypeByName )
    _method( LLVMDumpModule )
    _method( LLVMDisposeModule )
    _method( LLVMDumpModuleToString )
    _method( LLVMVerifyModule )
    _method( LLVMGetModuleFromAssembly )
    _method( LLVMGetModuleFromBitcode )
    _method( LLVMGetBitcodeFromModule )
    _method( LLVMGetNativeCodeFromModule )
    _method( LLVMModuleGetPointerSize )
    _method( LLVMModuleGetOrInsertFunction )
    _method( LLVMLinkModules )

    /* Types */

    /* General */
    _method( LLVMGetTypeKind )
    _method( LLVMDumpTypeToString )

    /* Integer types */
    _method( LLVMInt1Type )
    _method( LLVMInt8Type )
    _method( LLVMInt16Type )
    _method( LLVMInt32Type )
    _method( LLVMInt64Type )
    _method( LLVMIntType )
    _method( LLVMGetIntTypeWidth )

    /* Floating-point types */
    _method( LLVMFloatType )
    _method( LLVMDoubleType )
    _method( LLVMX86FP80Type )
    _method( LLVMFP128Type )
    _method( LLVMPPCFP128Type )

    /* Function types */
    _method( LLVMFunctionType )
    _method( LLVMIsFunctionVarArg )
    _method( LLVMGetReturnType )
    _method( LLVMCountParamTypes )
    _method( LLVMGetFunctionTypeParams )

    /* Struct types */
    _method( LLVMStructType )
    _method( LLVMStructTypeIdentified )
    _method( LLVMSetStructBody )
    _method( LLVMCountStructElementTypes )
    _method( LLVMGetStructElementTypes )
    _method( LLVMIsPackedStruct )
    _method( LLVMIsOpaqueStruct )
    _method( LLVMIsLiteralStruct )
    _method( LLVMGetStructName )
    _method( LLVMSetStructName )

    /* Array types */
    _method( LLVMArrayType )
    _method( LLVMGetElementType )
    _method( LLVMGetArrayLength )

    /* Pointer types */
    _method( LLVMPointerType )
    _method( LLVMGetPointerAddressSpace )

    /* Vector type */
    _method( LLVMVectorType )
    _method( LLVMGetVectorSize )

    /* Other types */
    _method( LLVMVoidType )
    _method( LLVMLabelType )

    /* Type handles */
    /*
    _method( LLVMResolveTypeHandle )
    _method( LLVMDisposeTypeHandle )
    */

    /* Values */

    /* Operations on all values */
    _method( LLVMTypeOf )
    _method( LLVMGetValueName )
    _method( LLVMSetValueName )
    _method( LLVMDumpValue )
    _method( LLVMDumpValueToString )
    _method( LLVMValueGetID )
    _method( LLVMValueGetNumUses )
    _method( LLVMValueGetUses )

    /* Users */

    _method( LLVMUserGetNumOperands )
    _method( LLVMUserGetOperand )

    /* Constant Values */

    /* Operations on constants of any type */
    _method( LLVMConstNull )
    _method( LLVMConstAllOnes )
    _method( LLVMGetUndef )
    _method( LLVMIsConstant )
    _method( LLVMIsNull )
    _method( LLVMIsUndef )

    /* Operations on scalar constants */
    _method( LLVMConstInt )
    _method( LLVMConstReal )
    _method( LLVMConstRealOfString )
    _method( LLVMConstIntGetZExtValue )
    _method( LLVMConstIntGetSExtValue )

    /* Operations on composite constants */
    _method( LLVMConstString )
    _method( LLVMConstArray )
    _method( LLVMConstStruct )
    _method( LLVMConstVector )

    /* Constant expressions */
    _method( LLVMGetConstExprOpcode )
    _method( LLVMGetConstExprOpcodeName )
    _method( LLVMSizeOf )
    _method( LLVMConstNeg )
    _method( LLVMConstNot )
    _method( LLVMConstAdd )
    _method( LLVMConstFAdd )
    _method( LLVMConstSub )
    _method( LLVMConstFSub )
    _method( LLVMConstMul )
    _method( LLVMConstFMul )
    _method( LLVMConstUDiv )
    _method( LLVMConstSDiv )
    _method( LLVMConstFDiv )
    _method( LLVMConstURem )
    _method( LLVMConstSRem )
    _method( LLVMConstFRem )
    _method( LLVMConstAnd )
    _method( LLVMConstOr )
    _method( LLVMConstXor )
    _method( LLVMConstICmp )
    _method( LLVMConstFCmp )
    _method( LLVMConstShl )
    _method( LLVMConstLShr )
    _method( LLVMConstAShr )
    _method( LLVMConstGEP )
    _method( LLVMConstTrunc )
    _method( LLVMConstSExt )
    _method( LLVMConstZExt )
    _method( LLVMConstFPTrunc )
    _method( LLVMConstFPExt )
    _method( LLVMConstUIToFP )
    _method( LLVMConstSIToFP )
    _method( LLVMConstFPToUI )
    _method( LLVMConstFPToSI )
    _method( LLVMConstPtrToInt )
    _method( LLVMConstIntToPtr )
    _method( LLVMConstBitCast )
    _method( LLVMConstSelect )
    _method( LLVMConstExtractElement )
    _method( LLVMConstInsertElement )
    _method( LLVMConstShuffleVector )

    /* Globals */

    /* Globals (general) */
    _method( LLVMGetGlobalParent )
    _method( LLVMIsDeclaration )
    _method( LLVMGetLinkage )
    _method( LLVMSetLinkage )
    _method( LLVMGetSection )
    _method( LLVMSetSection )
    _method( LLVMGetVisibility )
    _method( LLVMSetVisibility )
    _method( LLVMGetAlignment )
    _method( LLVMSetAlignment )

    /* Global Variables */
    _method( LLVMAddGlobal )
    _method( LLVMGetNamedGlobal )
    _method( LLVMGetFirstGlobal )
    _method( LLVMGetNextGlobal )
    _method( LLVMDeleteGlobal )
    _method( LLVMHasInitializer )
    _method( LLVMGetInitializer )
    _method( LLVMSetInitializer )
    _method( LLVMSetThreadLocal )
    _method( LLVMIsThreadLocal )
    _method( LLVMSetGlobalConstant )
    _method( LLVMIsGlobalConstant )

    /* Functions */
    _method( LLVMAddFunction )
    _method( LLVMGetNamedFunction )
    _method( LLVMGetFirstFunction )
    _method( LLVMGetNextFunction )
    _method( LLVMDeleteFunction )
    _method( LLVMGetIntrinsicID )
    _method( LLVMGetFunctionCallConv )
    _method( LLVMSetFunctionCallConv )
    _method( LLVMGetGC )
    _method( LLVMSetGC )
    _method( LLVMGetDoesNotThrow )
    _method( LLVMSetDoesNotThrow )
    _method( LLVMVerifyFunction )
    _method( LLVMViewFunctionCFG )
    _method( LLVMViewFunctionCFGOnly )
    _method( LLVMAddFunctionAttr )
    _method( LLVMRemoveFunctionAttr )

    /* Arguments */
    _method( LLVMCountParams )
    _method( LLVMGetFirstParam )
    _method( LLVMGetNextParam )
    _method( LLVMGetParamParent )
    _method( LLVMAddAttribute )
    _method( LLVMRemoveAttribute )
    _method( LLVMSetParamAlignment )
    _method( LLVMGetParamAlignment )

    /* Basic Blocks */
    _method( LLVMGetBasicBlockParent )
    _method( LLVMCountBasicBlocks )
    _method( LLVMGetFirstBasicBlock )
    _method( LLVMGetNextBasicBlock )
    _method( LLVMGetEntryBasicBlock )
    _method( LLVMAppendBasicBlock )
    _method( LLVMInsertBasicBlock )
    _method( LLVMDeleteBasicBlock )

    /* MetaData */
    _method( LLVMMetaDataGet )
    _method( LLVMGetNamedMetadataOperands )
    _method( LLVMAddNamedMetadataOperand )
    _method( LLVMMetaDataGetOperand )
    _method( LLVMMetaDataGetNumOperands )
    _method( LLVMMetaDataStringGet )

    /* Instructions */
    _method( LLVMGetInstructionParent )
    _method( LLVMGetFirstInstruction )
    _method( LLVMGetNextInstruction )
    _method( LLVMInstIsTerminator )
    _method( LLVMInstIsBinaryOp )
    _method( LLVMInstIsShift )
    _method( LLVMInstIsCast )
    _method( LLVMInstIsLogicalShift )
    _method( LLVMInstIsArithmeticShift )
    _method( LLVMInstIsAssociative )
    _method( LLVMInstIsCommutative )
    _method( LLVMInstIsVolatile )
    _method( LLVMSetVolatile )
    _method( LLVMInstGetOpcode )
    _method( LLVMInstGetOpcodeName )

    _method( LLVMInstSetMetaData )

    /* Call Sites (Call or Invoke) */
    _method( LLVMSetInstructionCallConv )
    _method( LLVMGetInstructionCallConv )
    _method( LLVMIsTailCall )
    _method( LLVMSetTailCall )
    _method( LLVMAddInstrAttribute )
    _method( LLVMRemoveInstrAttribute )
    _method( LLVMSetInstrParamAlignment )
    _method( LLVMInstGetCalledFunction )

    /* PHI Nodes */
    _method( LLVMAddIncoming1 )
    _method( LLVMCountIncoming )
    _method( LLVMGetIncomingValue )
    _method( LLVMGetIncomingBlock )

    /* Comparison Instructions */
    _method( LLVMCmpInstGetPredicate )

    /* Instruction builders */
    _method( LLVMCreateBuilder )
    _method( LLVMPositionBuilderBefore )
    _method( LLVMPositionBuilderAtEnd )
    _method( LLVMGetInsertBlock )
    _method( LLVMDisposeBuilder )

    /* Terminators */
    _method( LLVMBuildRetVoid )
    _method( LLVMBuildRet )
    _method( LLVMBuildRetMultiple )
    _method( LLVMBuildBr )
    _method( LLVMBuildCondBr )
    _method( LLVMBuildSwitch )
    _method( LLVMBuildInvoke )
    _method( LLVMBuildUnreachable )

    /* Add a case to the switch instruction */
    _method( LLVMAddCase )

    /* Arithmetic */
    _method( LLVMBuildAdd )
    _method( LLVMBuildFAdd)
    _method( LLVMBuildSub )
    _method( LLVMBuildFSub)
    _method( LLVMBuildMul )
    _method( LLVMBuildFMul)
    _method( LLVMBuildUDiv )
    _method( LLVMBuildSDiv )
    _method( LLVMBuildFDiv )
    _method( LLVMBuildURem )
    _method( LLVMBuildSRem )
    _method( LLVMBuildFRem )
    _method( LLVMBuildShl )
    _method( LLVMBuildLShr )
    _method( LLVMBuildAShr )
    _method( LLVMBuildAnd )
    _method( LLVMBuildOr )
    _method( LLVMBuildXor )
    _method( LLVMBuildNeg )
    _method( LLVMBuildNot )

    /* Memory */
    _method( LLVMBuildMalloc )
    _method( LLVMBuildArrayMalloc )
    _method( LLVMBuildAlloca )
    _method( LLVMBuildArrayAlloca )
    _method( LLVMBuildFree )
    _method( LLVMBuildLoad )
    _method( LLVMBuildStore )
    _method( LLVMBuildGEP )

    _method( LLVMLdSetAlignment )
    _method( LLVMStSetAlignment )

    /* Casts */
    _method( LLVMBuildTrunc )
    _method( LLVMBuildZExt )
    _method( LLVMBuildSExt )
    _method( LLVMBuildFPToUI )
    _method( LLVMBuildFPToSI )
    _method( LLVMBuildUIToFP )
    _method( LLVMBuildSIToFP )
    _method( LLVMBuildFPTrunc )
    _method( LLVMBuildFPExt )
    _method( LLVMBuildPtrToInt )
    _method( LLVMBuildIntToPtr )
    _method( LLVMBuildBitCast )

    /* Comparisons */
    _method( LLVMBuildICmp )
    _method( LLVMBuildFCmp )

    /* Atomics */
    _method( LLVMBuildAtomicCmpXchg )
    _method( LLVMBuildAtomicRMW )
    _method( LLVMBuildAtomicLoad )
    _method( LLVMBuildAtomicStore )
    _method( LLVMBuildFence )

    /* Miscellaneous instructions */
    _method( LLVMBuildGetResult )
    _method( LLVMBuildInsertValue )
    _method( LLVMBuildPhi )
    _method( LLVMBuildCall )
    _method( LLVMBuildSelect )
    _method( LLVMBuildVAArg )
    _method( LLVMBuildExtractElement )
    _method( LLVMBuildInsertElement )
    _method( LLVMBuildShuffleVector )

    /* Memory Buffer */
    _method( LLVMCreateMemoryBufferWithContentsOfFile )
    _method( LLVMCreateMemoryBufferWithSTDIN )
    _method( LLVMDisposeMemoryBuffer )

    /* Pass Manager Builder */

    _method( LLVMPassManagerBuilderCreate  )
    _method( LLVMPassManagerBuilderDispose )

    _method( LLVMPassManagerBuilderSetOptLevel )
    _method( LLVMPassManagerBuilderGetOptLevel )

    _method( LLVMPassManagerBuilderSetSizeLevel )
    _method( LLVMPassManagerBuilderGetSizeLevel )

    _method( LLVMPassManagerBuilderSetVectorize )
    _method( LLVMPassManagerBuilderGetVectorize )


    _method( LLVMPassManagerBuilderSetDisableUnitAtATime )
    _method( LLVMPassManagerBuilderGetDisableUnitAtATime )

    _method( LLVMPassManagerBuilderSetDisableUnrollLoops )
    _method( LLVMPassManagerBuilderGetDisableUnrollLoops )

    _method( LLVMPassManagerBuilderSetDisableSimplifyLibCalls )
    _method( LLVMPassManagerBuilderGetDisableSimplifyLibCalls )

    _method( LLVMPassManagerBuilderUseInlinerWithThreshold )

    _method( LLVMPassManagerBuilderPopulateFunctionPassManager )
    _method( LLVMPassManagerBuilderPopulateModulePassManager )

    /* Pass Manager */
    _method( LLVMCreatePassManager )
    _method( LLVMCreateFunctionPassManagerForModule )
    _method( LLVMRunPassManager )
    _method( LLVMInitializeFunctionPassManager )
    _method( LLVMRunFunctionPassManager )
    _method( LLVMFinalizeFunctionPassManager )
    _method( LLVMDisposePassManager )
    _method( LLVMDumpPasses )
    _method( LLVMAddPassByName )
    _method( LLVMInitializePasses )

    _method( LLVMInitializeNativeTarget )
    _method( LLVMInitializeNativeTargetAsmPrinter )
#if !defined(LLVM_DISABLE_PTX)
# if LLVM_HAS_NVPTX
    _method( LLVMInitializeNVPTXTarget )
    _method( LLVMInitializeNVPTXTargetInfo )
    _method( LLVMInitializeNVPTXTargetMC )
    _method( LLVMInitializeNVPTXAsmPrinter )
# else
    _method( LLVMInitializePTXTarget )
    _method( LLVMInitializePTXTargetInfo )
    _method( LLVMInitializePTXTargetMC )
    _method( LLVMInitializePTXAsmPrinter )
# endif
#endif
    /* Passes */

    /*
    _pass( AAEval )
    _pass( AggressiveDCE )
    _pass( AliasAnalysisCounter )
    _pass( AlwaysInliner )
    _pass( ArgumentPromotion )
    _pass( BasicAliasAnalysis )
    _pass( BlockPlacement )
    _pass( BreakCriticalEdges )
    _pass( CFGSimplification )
    _pass( CodeGenPrepare )
    _pass( ConstantMerge )
    _pass( ConstantPropagation )
    _pass( DbgInfoPrinter )
    _pass( DeadArgElimination )
    _pass( DeadCodeElimination )
    _pass( DeadInstElimination )
    _pass( DeadStoreElimination )
    _pass( DemoteRegisterToMemory )
    _pass( DomOnlyPrinter )
    _pass( DomOnlyViewer )
    _pass( DomPrinter )
    _pass( DomViewer )
    _pass( EdgeProfiler )
    _pass( FunctionAttrs )
    _pass( FunctionInlining )
    //_pass( GEPSplitter )
    _pass( GlobalDCE )
    _pass( GlobalOptimizer )
    _pass( GlobalsModRef )
    _pass( GVN )
    _pass( IndVarSimplify )
    _pass( InstCount )
    _pass( InstructionCombining )
    _pass( InstructionNamer )
    _pass( IPConstantPropagation )
    _pass( IPSCCP )
    _pass( JumpThreading )
    _pass( LazyValueInfo )
    _pass( LCSSA )
    _pass( LICM )
    //_pass( LiveValues )
    _pass( LoopDeletion )
    _pass( LoopDependenceAnalysis )
    _pass( LoopExtractor )
    //_pass( LoopIndexSplit )
    _pass( LoopRotate )
    _pass( LoopSimplify )
    _pass( LoopStrengthReduce )
    _pass( LoopUnroll )
    _pass( LoopUnswitch )
    _pass( LowerInvoke )
    _pass( LowerSwitch )
    _pass( MemCpyOpt )
    _pass( MergeFunctions )
    _pass( NoAA )
    _pass( NoProfileInfo )
    _pass( OptimalEdgeProfiler )
    _pass( PartialInlining )
    //_pass( PartialSpecialization )
    _pass( PostDomOnlyPrinter )
    _pass( PostDomOnlyViewer )
    _pass( PostDomPrinter )
    _pass( PostDomViewer )
    _pass( ProfileEstimator )
    _pass( ProfileLoader )
    _pass( ProfileVerifier )
    _pass( PromoteMemoryToRegister )
    _pass( PruneEH )
    _pass( Reassociate )
    _pass( ScalarEvolutionAliasAnalysis )
    _pass( ScalarReplAggregates )
    _pass( SCCP )
    //_pass( SimplifyHalfPowrLibCalls )
    _pass( SimplifyLibCalls )
    _pass( SingleLoopExtractor )
    _pass( StripDeadPrototypes )
    _pass( StripNonDebugSymbols )
    _pass( StripSymbols )
    //_pass( StructRetPromotion )
    _pass( TailCallElimination )
    //_pass( TailDuplication )
    _pass( UnifyFunctionExitNodes )

    _pass( Internalize2 )
    */

    /* Target Machine */
    _method( LLVMTargetMachineFromEngineBuilder )
    _method( LLVMDisposeTargetMachine )
    _method( LLVMTargetMachineLookup )
    _method( LLVMTargetMachineEmitFile )
    _method( LLVMTargetMachineGetTargetData )
    _method( LLVMTargetMachineGetTargetName )
    _method( LLVMTargetMachineGetTargetShortDescription )
    _method( LLVMTargetMachineGetTriple )
    _method( LLVMTargetMachineGetCPU )
    _method( LLVMTargetMachineGetFS )

    _method( LLVMPrintRegisteredTargetsForVersion )
    _method( LLVMGetHostCPUName )

    /* Target Data */
    _method( LLVMCreateTargetData )
    _method( LLVMDisposeTargetData )
    _method( LLVMTargetDataAsString )
    _method( LLVMAddTargetData )
    _method( LLVMByteOrder )
    _method( LLVMPointerSize )
    _method( LLVMIntPtrType )
    _method( LLVMSizeOfTypeInBits )
    _method( LLVMStoreSizeOfType )
    _method( LLVMABISizeOfType )
    _method( LLVMABIAlignmentOfType )
    _method( LLVMCallFrameAlignmentOfType )
    _method( LLVMPreferredAlignmentOfType )
    _method( LLVMPreferredAlignmentOfGlobal )
    _method( LLVMElementAtOffset )
    _method( LLVMOffsetOfElement )

    /* Engine Builder */

    _method( LLVMCreateEngineBuilder )
    _method( LLVMDisposeEngineBuilder )
    _method( LLVMEngineBuilderForceJIT )
    _method( LLVMEngineBuilderForceInterpreter )
    _method( LLVMEngineBuilderSetOptLevel )
    _method( LLVMEngineBuilderSetMCPU )
    _method( LLVMEngineBuilderSetMAttrs )
    _method( LLVMEngineBuilderCreate )

    /* Execution Engine */
    _method( LLVMCreateExecutionEngine )
    _method( LLVMDisposeExecutionEngine )
    _method( LLVMRunFunction2 )
    _method( LLVMGetPointerToFunction )
    _method( LLVMGetExecutionEngineTargetData )
    _method( LLVMRunStaticConstructors )
    _method( LLVMRunStaticDestructors )
    _method( LLVMFreeMachineCodeForFunction )
    _method( LLVMAddModule )
    _method( LLVMRemoveModule2 )

    /* Generic Value */
    _method( LLVMCreateGenericValueOfInt )
    _method( LLVMCreateGenericValueOfFloat )
    _method( LLVMCreateGenericValueOfPointer )
    _method( LLVMGenericValueToInt )
    _method( LLVMGenericValueToFloat )
    _method( LLVMGenericValueToPointer )
    _method( LLVMDisposeGenericValue )

    /* Misc */
    _method( LLVMGetIntrinsic )
    _method( LLVMLoadLibraryPermanently )
    _method( LLVMParseEnvOpts )

    _method( LLVMInlineFunction )
    _method( PyCObjectVoidPtrToPyLong )
    { NULL }
};



// Module main function, hairy because of py3k port
extern "C" {

#if (PY_MAJOR_VERSION >= 3)
struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "_core",
    NULL,
    -1,
    core_methods,
    NULL, NULL, NULL, NULL
};
#define INITERROR return NULL
PyObject *
PyInit__core(void)
#else
#define INITERROR return
PyMODINIT_FUNC
init_core(void)
#endif
{
    LLVMLinkInJIT();
    LLVMLinkInInterpreter();
    LLVMInitializeNativeTarget();
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create( &module_def );
#else
    PyObject *module = Py_InitModule("_core", core_methods);
#endif
    if (module == NULL)
        INITERROR;
#if PY_MAJOR_VERSION >= 3

    return module;
#endif
}

} // end extern C
