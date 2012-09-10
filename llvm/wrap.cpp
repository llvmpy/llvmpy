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

#include "wrap.h"

/*===----------------------------------------------------------------------===*/
/* Helper functions/macros                                                    */
/*===----------------------------------------------------------------------===*/

#define _define_std_ctor(typ)                   \
PyObject * ctor_ ## typ ( typ p)                \
{                                               \
    if (p){                                     \
        return PyCapsule_New(p, NULL, NULL);    \
    }                                           \
    Py_RETURN_NONE;                             \
}

/*===----------------------------------------------------------------------===*/
/* Type ctor/dtor                                                             */
/*===----------------------------------------------------------------------===*/

_define_std_ctor(LLVMModuleRef)
_define_std_ctor(LLVMTypeRef)
_define_std_ctor(LLVMValueRef)
_define_std_ctor(LLVMBasicBlockRef)
_define_std_ctor(LLVMBuilderRef)
_define_std_ctor(LLVMMemoryBufferRef)
_define_std_ctor(LLVMPassManagerRef)
_define_std_ctor(LLVMExecutionEngineRef)
_define_std_ctor(LLVMTargetDataRef)
_define_std_ctor(LLVMGenericValueRef)

_define_std_ctor(LLVMPassManagerBuilderRef)
_define_std_ctor(LLVMEngineBuilderRef)
_define_std_ctor(LLVMTargetMachineRef)

PyObject *ctor_int(int i)
{
    return PyLong_FromLong((long)i);
}

PyObject *ctor_llvmwrap_ull(llvmwrap_ull ull)
{
    return PyLong_FromUnsignedLongLong(ull);
}

PyObject *ctor_llvmwrap_ll(llvmwrap_ll ll)
{
    return PyLong_FromLongLong(ll);
}

/*===----------------------------------------------------------------------===*/
/* Helper functions                                                           */
/*===----------------------------------------------------------------------===*/

void *get_object_arg(PyObject *args)
{
    PyObject *o;

    if (!PyArg_ParseTuple(args, "O", &o))
        return NULL;

    return PyCapsule_GetPointer(o, NULL);
}

// must delete [] returned array
void **make_array_from_list(PyObject *list, int n)
{
    void **arr = new void*[n] ;
    if (!arr)
        return NULL;

    int i;
    for (i=0; i<n; i++) {
        PyObject *e = PyList_GetItem(list, i);
        arr[i] = PyCapsule_GetPointer(e, NULL);
    }

    return arr;
}

#define LIST_FROM_ARRAY_IMPL(TYPE)                                  \
PyObject *make_list_from_ ## TYPE ## _array( TYPE *p, unsigned n)   \
{                                                                   \
    size_t i;                                                       \
    PyObject *list = PyList_New(n);                                 \
                                                                    \
    if (!list)                                                      \
        return NULL;                                                \
                                                                    \
    for (i=0; i<n; i++) {                                           \
        PyObject *elem = ctor_ ## TYPE (p[i]);                      \
        PyList_SetItem(list, i, elem);                              \
    }                                                               \
                                                                    \
    return list;                                                    \
}

LIST_FROM_ARRAY_IMPL(LLVMTypeRef)
LIST_FROM_ARRAY_IMPL(LLVMValueRef)

