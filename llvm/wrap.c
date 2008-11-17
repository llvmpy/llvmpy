/*
 * Copyright (c) 2008, Mahadevan R All rights reserved.
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

