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

template <> PyObject* pycap_new<unsigned PY_LONG_LONG>(unsigned PY_LONG_LONG ull)
{
    return PyLong_FromUnsignedLongLong(ull);
}

template <> PyObject* pycap_new<PY_LONG_LONG>(PY_LONG_LONG ll)
{
    return PyLong_FromLongLong(ll);
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

_wrap_obj2str(LLVMGetDataLayout, LLVMModuleRef)
_wrap_objstr2none(LLVMSetDataLayout, LLVMModuleRef)
_wrap_obj2str(LLVMGetModuleIdentifier, LLVMModuleRef)
_wrap_objstr2none(LLVMSetModuleIdentifier, LLVMModuleRef)
_wrap_obj2str(LLVMGetTarget, LLVMModuleRef)
_wrap_objstr2none(LLVMSetTarget, LLVMModuleRef)
_wrap_objstr2none(LLVMModuleAddLibrary, LLVMModuleRef)
_wrap_objstr2obj(LLVMGetTypeByName, LLVMModuleRef, LLVMTypeRef)
_wrap_obj2none(LLVMDumpModule, LLVMModuleRef)
_wrap_obj2none(LLVMDisposeModule, LLVMModuleRef)
_wrap_dumper(LLVMDumpModuleToString, LLVMModuleRef)
 _wrap_obj2obj( LLVMModuleGetPointerSize, LLVMModuleRef, int)
_wrap_objstrobj2obj(LLVMModuleGetOrInsertFunction, LLVMModuleRef,
                    LLVMTypeRef, LLVMValueRef)

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
#if (PY_MAJOR_VERSION >= 3)
    if ( !PyArg_ParseTuple(args, "y", &str) ){
#else
    if ( !PyArg_ParseTuple(args, "s", &str) ){
#endif
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
    const unsigned char *ubytes = LLVMGetBitcodeFromModule(m, &len) ;
    if ( !ubytes ) Py_RETURN_NONE;

    const char *chars = reinterpret_cast<const char*>(ubytes) ;
    PyObject *ret = PyBytes_FromStringAndSize(chars, len);
    delete [] ubytes;
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

    delete [] ubytes;

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

    PyObject *ret = NULL;
    char *errmsg = NULL;
    if (LLVMLinkModules(dest, src, (LLVMLinkerMode)mode, &errmsg)) {
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

_wrap_objstr2obj(LLVMModuleGetOrInsertNamedMetaData, LLVMModuleRef, LLVMNamedMDRef)
_wrap_objstr2obj(LLVMModuleGetNamedMetaData, LLVMModuleRef, LLVMNamedMDRef)
_wrap_obj2obj(LLVMCloneModule, LLVMModuleRef, LLVMModuleRef)

/*===----------------------------------------------------------------------===*/
/* Types                                                                      */
/*===----------------------------------------------------------------------===*/

/*===-- General ----------------------------------------------------------===*/

_wrap_obj2obj(LLVMGetTypeKind, LLVMTypeRef, int)
_wrap_dumper(LLVMDumpTypeToString, LLVMTypeRef)

/*===-- Integer types ----------------------------------------------------===*/

_wrap_none2obj(LLVMInt1Type, LLVMTypeRef)
_wrap_none2obj(LLVMInt8Type, LLVMTypeRef)
_wrap_none2obj(LLVMInt16Type, LLVMTypeRef)
_wrap_none2obj(LLVMInt32Type, LLVMTypeRef)
_wrap_none2obj(LLVMInt64Type, LLVMTypeRef)
_wrap_int2obj(LLVMIntType, LLVMTypeRef)
_wrap_obj2obj(LLVMGetIntTypeWidth, LLVMTypeRef, int)

/*===-- Floating-point types ---------------------------------------------===*/

_wrap_none2obj(LLVMFloatType, LLVMTypeRef)
_wrap_none2obj(LLVMDoubleType, LLVMTypeRef)
_wrap_none2obj(LLVMX86FP80Type, LLVMTypeRef)
_wrap_none2obj(LLVMFP128Type, LLVMTypeRef)
_wrap_none2obj(LLVMPPCFP128Type, LLVMTypeRef)

/*===-- Function types ---------------------------------------------------===*/

_wrap_objlistint2obj(LLVMFunctionType, LLVMTypeRef, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMIsFunctionVarArg, LLVMTypeRef, int)
_wrap_obj2obj(LLVMGetReturnType, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMCountParamTypes, LLVMTypeRef, int)

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

_wrap_listint2obj(LLVMStructType, LLVMTypeRef, LLVMTypeRef)
_wrap_str2obj(LLVMStructTypeIdentified, LLVMTypeRef)
_wrap_objlistint2none(LLVMSetStructBody, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMCountStructElementTypes, LLVMTypeRef, int)
_wrap_obj2str(LLVMGetStructName, LLVMTypeRef)
_wrap_objstr2none(LLVMSetStructName, LLVMTypeRef)


static PyObject *
_wLLVMGetStructElementTypes(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    return obj2arr(self, args, LLVMCountStructElementTypes,
            LLVMGetStructElementTypes);
    LLVMPY_CATCH_ALL
}


_wrap_obj2obj(LLVMIsPackedStruct, LLVMTypeRef, int)
_wrap_obj2obj(LLVMIsOpaqueStruct, LLVMTypeRef, int)
_wrap_obj2obj(LLVMIsLiteralStruct, LLVMTypeRef, int)

/*===-- Array types ------------------------------------------------------===*/

_wrap_objint2obj(LLVMArrayType, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMGetElementType, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMGetArrayLength, LLVMTypeRef, int)

/*===-- Pointer types ----------------------------------------------------===*/

_wrap_objint2obj(LLVMPointerType, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMGetPointerAddressSpace, LLVMTypeRef, int)

/*===-- Vector type ------------------------------------------------------===*/

_wrap_objint2obj(LLVMVectorType, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMGetVectorSize, LLVMTypeRef, int)

/*===-- Other types ------------------------------------------------------===*/

_wrap_none2obj(LLVMVoidType, LLVMTypeRef)
_wrap_none2obj(LLVMLabelType, LLVMTypeRef)

/*===-- Type handles -----------------------------------------------------===*/

/*
_wrap_obj2obj(LLVMCreateTypeHandle, LLVMTypeRef, LLVMTypeHandleRef)
_wrap_obj2obj(LLVMResolveTypeHandle, LLVMTypeHandleRef, LLVMTypeRef)
_wrap_obj2none(LLVMDisposeTypeHandle, LLVMTypeHandleRef)
*/


/*===----------------------------------------------------------------------===*/
/* Values                                                                     */
/*===----------------------------------------------------------------------===*/

/* Operations on all values */

_wrap_obj2obj(LLVMTypeOf, LLVMValueRef, LLVMTypeRef)
_wrap_obj2str(LLVMGetValueName, LLVMValueRef)
_wrap_objstr2none(LLVMSetValueName, LLVMValueRef)
_wrap_obj2none(LLVMDumpValue, LLVMValueRef)
_wrap_dumper(LLVMDumpValueToString, LLVMValueRef)
_wrap_obj2obj(LLVMValueGetID, LLVMValueRef, int)
_wrap_obj2obj(LLVMValueGetNumUses, LLVMValueRef, int)

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

_wrap_obj2obj(LLVMUserGetNumOperands, LLVMValueRef, int)
_wrap_objint2obj(LLVMUserGetOperand,  LLVMValueRef, LLVMValueRef)

/*===-- Constant Values --------------------------------------------------===*/

/* Operations on constants of any type */

_wrap_obj2obj(LLVMConstNull, LLVMTypeRef, LLVMValueRef)
_wrap_obj2obj(LLVMConstAllOnes, LLVMTypeRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetUndef, LLVMTypeRef, LLVMValueRef)
_wrap_obj2obj(LLVMIsConstant, LLVMValueRef, int)
_wrap_obj2obj(LLVMIsNull, LLVMValueRef, int)
_wrap_obj2obj(LLVMIsUndef, LLVMValueRef, int)

/* Operations on scalar constants */

static PyObject *
_wLLVMConstInt(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj;
    unsigned PY_LONG_LONG n;
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

_wrap_objstr2obj(LLVMConstRealOfString, LLVMTypeRef, LLVMValueRef)
_wrap_obj2obj(LLVMConstIntGetZExtValue, LLVMValueRef, llvmwrap_ull)
_wrap_obj2obj(LLVMConstIntGetSExtValue, LLVMValueRef, llvmwrap_ll)

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

_wrap_objlist2obj(LLVMConstArray, LLVMTypeRef, LLVMValueRef, LLVMValueRef)
_wrap_listint2obj(LLVMConstStruct, LLVMValueRef, LLVMValueRef)
_wrap_list2obj(LLVMConstVector, LLVMValueRef, LLVMValueRef)

/* Constant expressions */

_wrap_obj2obj(LLVMGetConstExprOpcode, LLVMValueRef, int)
_wrap_obj2str(LLVMGetConstExprOpcodeName, LLVMValueRef)
_wrap_obj2obj(LLVMSizeOf, LLVMTypeRef, LLVMValueRef)
_wrap_obj2obj(LLVMConstNeg, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMConstNot, LLVMValueRef, LLVMValueRef)

_wrap_objobj2obj(LLVMConstAdd, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFAdd, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSub, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFSub, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstMul, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFMul, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstUDiv, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSDiv, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFDiv, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstURem, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSRem, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFRem, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstAnd, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstOr, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstXor, LLVMValueRef, LLVMValueRef, LLVMValueRef)

_wrap_enumobjobj2obj(LLVMConstICmp, LLVMIntPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_enumobjobj2obj(LLVMConstFCmp, LLVMRealPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef)

_wrap_objobj2obj(LLVMConstShl, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstLShr, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstAShr, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objlist2obj(LLVMConstGEP, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstTrunc, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSExt, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstZExt, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFPTrunc, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFPExt, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstUIToFP, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSIToFP, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFPToUI, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFPToSI, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstPtrToInt, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstIntToPtr, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstBitCast, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobj2obj(LLVMConstSelect, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstExtractElement, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobj2obj(LLVMConstInsertElement, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobj2obj(LLVMConstShuffleVector, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)


/*===----------------------------------------------------------------------===*/
/* Globals                                                                    */
/*===----------------------------------------------------------------------===*/

/*===-- Globals ----------------------------------------------------------===*/

_wrap_obj2obj(LLVMGetGlobalParent, LLVMValueRef, LLVMModuleRef)
_wrap_obj2obj(LLVMIsDeclaration, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetLinkage, LLVMValueRef, int)
_wrap_objenum2none(LLVMSetLinkage, LLVMValueRef, LLVMLinkage)
_wrap_obj2str(LLVMGetSection, LLVMValueRef)
_wrap_objstr2none(LLVMSetSection, LLVMValueRef)
_wrap_obj2obj(LLVMGetVisibility, LLVMValueRef, int)
_wrap_objenum2none(LLVMSetVisibility, LLVMValueRef, LLVMVisibility)
_wrap_obj2obj(LLVMGetAlignment, LLVMValueRef, int)
_wrap_objint2none(LLVMSetAlignment, LLVMValueRef)

/*===-- Global Variables -------------------------------------------------===*/
    
_wrap_objobjstr2obj(LLVMAddGlobal, LLVMModuleRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjstrint2obj(LLVMAddGlobalInAddressSpace, LLVMModuleRef, LLVMTypeRef, LLVMValueRef)
_wrap_objstr2obj(LLVMGetNamedGlobal, LLVMModuleRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetFirstGlobal, LLVMModuleRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetNextGlobal, LLVMValueRef, LLVMValueRef)
_wrap_obj2none(LLVMDeleteGlobal, LLVMValueRef)
_wrap_obj2obj(LLVMHasInitializer, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetInitializer, LLVMValueRef, LLVMValueRef)
_wrap_objobj2none(LLVMSetInitializer, LLVMValueRef, LLVMValueRef)
_wrap_objint2none(LLVMSetGlobalConstant, LLVMValueRef)
_wrap_obj2obj(LLVMIsGlobalConstant, LLVMValueRef, int)
_wrap_objint2none(LLVMSetThreadLocal, LLVMValueRef)
_wrap_obj2obj(LLVMIsThreadLocal, LLVMValueRef, int)


/*===-- Functions --------------------------------------------------------===*/

_wrap_objstrobj2obj(LLVMAddFunction, LLVMModuleRef, LLVMTypeRef, LLVMValueRef)
_wrap_objstr2obj(LLVMGetNamedFunction, LLVMModuleRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetFirstFunction, LLVMModuleRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetNextFunction, LLVMValueRef, LLVMValueRef)
_wrap_obj2none(LLVMDeleteFunction, LLVMValueRef)
_wrap_obj2obj(LLVMGetIntrinsicID, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetFunctionCallConv, LLVMValueRef, int)
_wrap_objint2none(LLVMSetFunctionCallConv, LLVMValueRef)
_wrap_obj2str(LLVMGetGC, LLVMValueRef)
_wrap_objstr2none(LLVMSetGC, LLVMValueRef)
_wrap_obj2obj(LLVMGetDoesNotThrow, LLVMValueRef, int)
_wrap_objint2none(LLVMSetDoesNotThrow, LLVMValueRef)
_wrap_obj2none(LLVMViewFunctionCFG, LLVMValueRef)
_wrap_obj2none(LLVMViewFunctionCFGOnly, LLVMValueRef)
_wrap_objenum2none(LLVMAddFunctionAttr, LLVMValueRef, LLVMAttribute)
_wrap_objenum2none(LLVMRemoveFunctionAttr, LLVMValueRef, LLVMAttribute)

static PyObject *
_wLLVMVerifyFunction(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    const LLVMValueRef fn = get_object_arg<LLVMValueRef>(args);
    if (!fn) return NULL;

    return pycap_new<int>(LLVMVerifyFunction(fn, LLVMReturnStatusAction));
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMGetFunctionFromInlineAsm(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *pycapFuncType;
    const char *inlineAsm = NULL;
    const char *constrains = NULL;
    int hasSideEffect;
    int isAlignStack;
    int asmDialect;

    if (!PyArg_ParseTuple(args, "Ossiii", &pycapFuncType, &inlineAsm,
                          &constrains, &hasSideEffect,
                          &isAlignStack, &asmDialect))
        return NULL;


    LLVMTypeRef funcType = pycap_get<LLVMTypeRef>(pycapFuncType);
    LLVMValueRef inlineAsmRef;
    inlineAsmRef = LLVMGetFunctionFromInlineAsm(funcType, inlineAsm, constrains,
                                                hasSideEffect, isAlignStack,
                                                asmDialect);

    return pycap_new<LLVMValueRef>(inlineAsmRef);
    LLVMPY_CATCH_ALL
}


/*===-- Arguments --------------------------------------------------------===*/

_wrap_obj2obj(LLVMCountParams, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetFirstParam, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetNextParam, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetParamParent, LLVMValueRef, LLVMValueRef)
_wrap_objenum2none(LLVMAddAttribute, LLVMValueRef, LLVMAttribute)
_wrap_objenum2none(LLVMRemoveAttribute, LLVMValueRef, LLVMAttribute)
_wrap_objenum2none(LLVMSetParamAlignment, LLVMValueRef, LLVMAttribute)
_wrap_obj2obj(LLVMGetParamAlignment, LLVMValueRef, int)

/*===-- Basic Blocks -----------------------------------------------------===*/

_wrap_obj2obj(LLVMGetBasicBlockParent, LLVMBasicBlockRef, LLVMValueRef)
_wrap_obj2obj(LLVMCountBasicBlocks, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetFirstBasicBlock, LLVMValueRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMGetNextBasicBlock, LLVMBasicBlockRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMGetEntryBasicBlock, LLVMValueRef, LLVMBasicBlockRef)
_wrap_objstr2obj(LLVMAppendBasicBlock, LLVMValueRef, LLVMBasicBlockRef)
_wrap_objstr2obj(LLVMInsertBasicBlock, LLVMBasicBlockRef, LLVMBasicBlockRef)
_wrap_obj2none(LLVMDeleteBasicBlock, LLVMBasicBlockRef)


/*===-- MetaData -----------------------------------------------------===*/

_wrap_objlist2obj(LLVMMetaDataGet, LLVMModuleRef, LLVMValueRef, LLVMValueRef)
_wrap_objstrobj2none(LLVMAddNamedMetadataOperand, LLVMModuleRef, LLVMValueRef)
_wrap_objint2obj(LLVMMetaDataGetOperand, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMMetaDataGetNumOperands, LLVMValueRef, int)
_wrap_objstr2obj(LLVMMetaDataStringGet, LLVMModuleRef, LLVMValueRef)

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


/*===-- NamedMetaData -----------------------------------------------------===*/

_wrap_obj2str( LLVMNamedMetaDataGetName, LLVMNamedMDRef )
_wrap_objobj2none( LLVMNamedMetaDataAddOperand, LLVMNamedMDRef, LLVMValueRef )
_wrap_obj2none( LLVMEraseNamedMetaData, LLVMNamedMDRef )
_wrap_dumper(LLVMDumpNamedMDToString, LLVMNamedMDRef)

/*===-- Instructions -----------------------------------------------------===*/

_wrap_obj2obj(LLVMGetInstructionParent, LLVMValueRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMGetFirstInstruction, LLVMBasicBlockRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetNextInstruction, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMInstIsTerminator,   LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsBinaryOp,     LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsShift,        LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsCast,         LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsLogicalShift, LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsArithmeticShift, LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsAssociative,  LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsCommutative,  LLVMValueRef, int)
_wrap_obj2obj(LLVMInstIsVolatile,     LLVMValueRef, int)
_wrap_objint2none(LLVMSetVolatile,    LLVMValueRef)
_wrap_obj2obj(LLVMInstGetOpcode,      LLVMValueRef, int)
_wrap_obj2str(LLVMInstGetOpcodeName,  LLVMValueRef)

_wrap_objstrobj2none(LLVMInstSetMetaData, LLVMValueRef, LLVMValueRef)
_wrap_obj2none(LLVMInstructionEraseFromParent,    LLVMValueRef)

/*===-- Call Sites (Call or Invoke) --------------------------------------===*/

_wrap_objint2none(LLVMSetInstructionCallConv, LLVMValueRef)
_wrap_obj2obj(LLVMGetInstructionCallConv, LLVMValueRef, int)
_wrap_objintenum2none(LLVMAddInstrAttribute, LLVMValueRef, LLVMAttribute)
_wrap_objintenum2none(LLVMRemoveInstrAttribute, LLVMValueRef, LLVMAttribute)
_wrap_objintint2none(LLVMSetInstrParamAlignment, LLVMValueRef)
_wrap_obj2obj(LLVMIsTailCall, LLVMValueRef, int)
_wrap_objint2none(LLVMSetTailCall, LLVMValueRef)
_wrap_obj2obj(LLVMInstGetCalledFunction, LLVMValueRef, LLVMValueRef)
_wrap_objobj2none(LLVMInstSetCalledFunction, LLVMValueRef, LLVMValueRef)

/*===-- PHI Nodes --------------------------------------------------------===*/

static void LLVMAddIncoming1(LLVMValueRef PhiNode, LLVMValueRef IncomingValue, LLVMBasicBlockRef IncomingBlock)
{
    LLVMAddIncoming(PhiNode, &IncomingValue, &IncomingBlock, 1);
}

_wrap_objobjobj2none(LLVMAddIncoming1, LLVMValueRef, LLVMValueRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMCountIncoming,       LLVMValueRef, int)
_wrap_objint2obj(LLVMGetIncomingValue, LLVMValueRef, LLVMValueRef)
_wrap_objint2obj(LLVMGetIncomingBlock, LLVMValueRef, LLVMBasicBlockRef)

/*===-- Compare Instructions ---------------------------------------------===*/

_wrap_obj2obj(LLVMCmpInstGetPredicate, LLVMValueRef, int)

/*===-- Instruction builders ----------------------------------------------===*/

_wrap_none2obj(LLVMCreateBuilder, LLVMBuilderRef)
_wrap_objobj2none(LLVMPositionBuilderBefore, LLVMBuilderRef, LLVMValueRef)
_wrap_objobj2none(LLVMPositionBuilderAtEnd, LLVMBuilderRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMGetInsertBlock, LLVMBuilderRef, LLVMBasicBlockRef)
_wrap_obj2none(LLVMDisposeBuilder, LLVMBuilderRef)

/* Terminators */

_wrap_obj2obj(LLVMBuildRetVoid, LLVMBuilderRef, LLVMValueRef)
_wrap_objobj2obj(LLVMBuildRet, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objlist2obj(LLVMBuildRetMultiple, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMBuildBr, LLVMBuilderRef, LLVMBasicBlockRef, LLVMValueRef)
_wrap_objobjobjobj2obj(LLVMBuildCondBr, LLVMBuilderRef, LLVMValueRef, LLVMBasicBlockRef, LLVMBasicBlockRef, LLVMValueRef)
_wrap_objobjobjint2obj(LLVMBuildSwitch, LLVMBuilderRef, LLVMValueRef, LLVMBasicBlockRef, LLVMValueRef)

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

_wrap_obj2obj(LLVMBuildUnreachable, LLVMBuilderRef, LLVMValueRef)

/* Add a case to the switch instruction */

_wrap_objobjobj2none(LLVMAddCase, LLVMValueRef, LLVMValueRef, LLVMBasicBlockRef)

/* Arithmetic */

_wrap_objobjobjstr2obj(LLVMBuildAdd, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFAdd, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildSub, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFSub, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildMul, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFMul, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildUDiv, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildSDiv, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFDiv, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildURem, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildSRem, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFRem, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildShl, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildLShr, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildAShr, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildAnd, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildOr, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildXor, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjstr2obj(LLVMBuildNeg, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjstr2obj(LLVMBuildNot, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)

/* Memory */

_wrap_objobjstr2obj(LLVMBuildMalloc, LLVMBuilderRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildArrayMalloc, LLVMBuilderRef, LLVMTypeRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjstr2obj(LLVMBuildAlloca, LLVMBuilderRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildArrayAlloca, LLVMBuilderRef, LLVMTypeRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMBuildFree, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjstr2obj(LLVMBuildLoad, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobj2obj(LLVMBuildStore, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjliststr2obj(LLVMBuildGEP, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjliststr2obj(LLVMBuildInBoundsGEP, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)



_wrap_objint2none(LLVMLdSetAlignment, LLVMValueRef)
_wrap_objint2none(LLVMStSetAlignment, LLVMValueRef)

/* Casts */

_wrap_objobjobjstr2obj(LLVMBuildTrunc, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildZExt, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildSExt, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFPToUI, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFPToSI, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildUIToFP, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildSIToFP, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFPTrunc, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildFPExt, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildPtrToInt, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildIntToPtr, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildBitCast, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)

/* Comparisons */

_wrap_objenumobjobjstr2obj(LLVMBuildICmp, LLVMBuilderRef, LLVMIntPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objenumobjobjstr2obj(LLVMBuildFCmp, LLVMBuilderRef, LLVMRealPredicate, LLVMValueRef, LLVMValueRef, LLVMValueRef)


/* Atomics */
_wrap_objobjobjobjstrint2obj(LLVMBuildAtomicCmpXchg, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objstrobjobjstrint2obj(LLVMBuildAtomicRMW, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjintstrint2obj(LLVMBuildAtomicLoad, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjintstrint2obj(LLVMBuildAtomicStore, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objstrint2obj(LLVMBuildFence, LLVMBuilderRef, LLVMValueRef)

/* Miscellaneous instructions */

_wrap_objobjintstr2obj(LLVMBuildGetResult, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjintstr2obj(LLVMBuildInsertValue, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjstr2obj(LLVMBuildPhi, LLVMBuilderRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjliststr2obj(LLVMBuildCall, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjobjstr2obj(LLVMBuildSelect, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildVAArg, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildExtractElement, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjobjstr2obj(LLVMBuildInsertElement, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjobjstr2obj(LLVMBuildShuffleVector, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)


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

_wrap_obj2none(LLVMDisposeMemoryBuffer, LLVMMemoryBufferRef)


/*===----------------------------------------------------------------------===*/
/* Pass Manager Builder                                                       */
/*===----------------------------------------------------------------------===*/

_wrap_none2obj(LLVMPassManagerBuilderCreate, LLVMPassManagerBuilderRef)
_wrap_obj2none(LLVMPassManagerBuilderDispose, LLVMPassManagerBuilderRef)

_wrap_objint2none(LLVMPassManagerBuilderSetOptLevel, LLVMPassManagerBuilderRef)
_wrap_obj2obj(LLVMPassManagerBuilderGetOptLevel, LLVMPassManagerBuilderRef, int)

_wrap_objint2none(LLVMPassManagerBuilderSetSizeLevel, LLVMPassManagerBuilderRef)
_wrap_obj2obj(LLVMPassManagerBuilderGetSizeLevel, LLVMPassManagerBuilderRef, int)

_wrap_objint2none(LLVMPassManagerBuilderSetVectorize, LLVMPassManagerBuilderRef)
_wrap_obj2obj(LLVMPassManagerBuilderGetVectorize, LLVMPassManagerBuilderRef, int)

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
_wrap_objint2none(LLVMPassManagerBuilderSetLoopVectorize, LLVMPassManagerBuilderRef)
_wrap_obj2obj(LLVMPassManagerBuilderGetLoopVectorize, LLVMPassManagerBuilderRef, int)
#endif //llvm-3.2

_wrap_objint2none(LLVMPassManagerBuilderSetDisableUnitAtATime,
                  LLVMPassManagerBuilderRef)
_wrap_obj2obj(LLVMPassManagerBuilderGetDisableUnitAtATime,
              LLVMPassManagerBuilderRef, int)

_wrap_objint2none(LLVMPassManagerBuilderSetDisableUnrollLoops,
                  LLVMPassManagerBuilderRef)
_wrap_obj2obj(LLVMPassManagerBuilderGetDisableUnrollLoops,
              LLVMPassManagerBuilderRef, int)

_wrap_objint2none(LLVMPassManagerBuilderSetDisableSimplifyLibCalls,
                  LLVMPassManagerBuilderRef)
_wrap_obj2obj(LLVMPassManagerBuilderGetDisableSimplifyLibCalls,
              LLVMPassManagerBuilderRef, int)

_wrap_objint2none(LLVMPassManagerBuilderUseInlinerWithThreshold,
                  LLVMPassManagerBuilderRef)


_wrap_objobj2none(LLVMPassManagerBuilderPopulateFunctionPassManager,
                  LLVMPassManagerBuilderRef,
                  LLVMPassManagerRef)

_wrap_objobj2none(LLVMPassManagerBuilderPopulateModulePassManager,
                  LLVMPassManagerBuilderRef,
                  LLVMPassManagerRef)


/*===----------------------------------------------------------------------===*/
/* Pass Manager                                                               */
/*===----------------------------------------------------------------------===*/

_wrap_none2obj(LLVMCreatePassManager, LLVMPassManagerRef)
_wrap_obj2obj(LLVMCreateFunctionPassManagerForModule, LLVMModuleRef, LLVMPassManagerRef)
_wrap_objobj2obj(LLVMRunPassManager, LLVMPassManagerRef, LLVMModuleRef, int)
_wrap_obj2obj(LLVMInitializeFunctionPassManager, LLVMPassManagerRef, int)
_wrap_objobj2obj(LLVMRunFunctionPassManager, LLVMPassManagerRef, LLVMValueRef, int)
_wrap_obj2obj(LLVMFinalizeFunctionPassManager, LLVMPassManagerRef, int)
_wrap_obj2none(LLVMDisposePassManager, LLVMPassManagerRef)
_wrap_none2str(LLVMDumpPasses)
_wrap_objstr2obj(LLVMAddPassByName, LLVMPassManagerRef, int)


_wrap_objobj2none(LLVMAddPass, LLVMPassManagerRef, LLVMPassRef)
_wrap_none2none(LLVMInitializePasses)

_wrap_none2obj(LLVMInitializeNativeTarget, int)
_wrap_none2obj(LLVMInitializeNativeTargetAsmPrinter, int)
#if !defined(LLVM_DISABLE_PTX)
# if LLVM_HAS_NVPTX
_wrap_none2none(LLVMInitializeNVPTXTarget)
_wrap_none2none(LLVMInitializeNVPTXTargetInfo)
_wrap_none2none( LLVMInitializeNVPTXTargetMC )
_wrap_none2none(LLVMInitializeNVPTXAsmPrinter)
# else
_wrap_none2none(LLVMInitializePTXTarget)
_wrap_none2none(LLVMInitializePTXTargetInfo)
_wrap_none2none( LLVMInitializePTXTargetMC )
_wrap_none2none(LLVMInitializePTXAsmPrinter)
# endif
#endif

/*===----------------------------------------------------------------------===*/
/* Passes                                                                     */
/*===----------------------------------------------------------------------===*/

_wrap_str2obj(LLVMCreatePassByName, LLVMPassRef)
_wrap_obj2none(LLVMDisposePass, LLVMPassRef)
_wrap_obj2str(LLVMGetPassName, LLVMPassRef)
_wrap_obj2none(LLVMPassDump, LLVMPassRef)

_wrap_str2obj(LLVMCreateTargetLibraryInfo, LLVMPassRef)

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
_wrap_obj2obj(LLVMCreateTargetTransformInfo, LLVMTargetMachineRef, LLVMPassRef)
#endif


/*===----------------------------------------------------------------------===*/
/* Target Machine                                                             */
/*===----------------------------------------------------------------------===*/

_wrap_none2str(LLVMGetHostCPUName);

_wrap_obj2obj(LLVMTargetMachineFromEngineBuilder, LLVMEngineBuilderRef,
              LLVMTargetMachineRef)
_wrap_obj2none(LLVMDisposeTargetMachine, LLVMTargetMachineRef)

static PyObject *
_wLLVMTargetMachineLookup(PyObject * self, PyObject * args)
{
    LLVMPY_TRY
    const char *triple;
    const char *cpu;
    const char *features;
    int opt, codemodel;

    if (!PyArg_ParseTuple(args, "sssii", &triple, &cpu, &features,
                          &opt, &codemodel))
        return NULL;

    std::string error;
    LLVMTargetMachineRef tm = LLVMTargetMachineLookup(triple, cpu, features,
                                                      opt, codemodel, error);
    if(!error.empty()){
        PyErr_SetString(PyExc_RuntimeError, error.c_str());
        return NULL;
    }
    return pycap_new<LLVMTargetMachineRef>(tm);
    LLVMPY_CATCH_ALL
}


static PyObject *
_wLLVMCreateTargetMachine(PyObject * self, PyObject * args)
{
    LLVMPY_TRY
    const char *triple;
    const char *cpu;
    const char *features;
    int opt, codemodel;

    if (!PyArg_ParseTuple(args, "sssii", &triple, &cpu, &features,
                                         &opt, &codemodel))
        return NULL;

    std::string error;
    LLVMTargetMachineRef tm = LLVMCreateTargetMachine(triple, cpu, features,
                                                      opt, codemodel, error);
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

_wrap_obj2obj(LLVMTargetMachineGetTargetData, LLVMTargetMachineRef,
              LLVMTargetDataRef)
_wrap_obj2str(LLVMTargetMachineGetTargetName, LLVMTargetMachineRef)
_wrap_obj2str(LLVMTargetMachineGetTargetShortDescription, LLVMTargetMachineRef)
_wrap_obj2str(LLVMTargetMachineGetTriple, LLVMTargetMachineRef)
_wrap_obj2str(LLVMTargetMachineGetCPU, LLVMTargetMachineRef)
_wrap_obj2str(LLVMTargetMachineGetFS, LLVMTargetMachineRef)
_wrap_none2none(LLVMPrintRegisteredTargetsForVersion)


/*===----------------------------------------------------------------------===*/
/* Target Data                                                                */
/*===----------------------------------------------------------------------===*/

_wrap_str2obj(LLVMCreateTargetData, LLVMTargetDataRef)
_wrap_obj2none(LLVMDisposeTargetData, LLVMTargetDataRef)

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

_wrap_objobj2none(LLVMAddTargetData, LLVMTargetDataRef, LLVMPassManagerRef)
_wrap_obj2obj(LLVMByteOrder, LLVMTargetDataRef, int)
_wrap_obj2obj(LLVMPointerSize, LLVMTargetDataRef, int)
_wrap_obj2obj(LLVMIntPtrType, LLVMTargetDataRef, LLVMTypeRef)
_wrap_objobj2obj(LLVMSizeOfTypeInBits, LLVMTargetDataRef, LLVMTypeRef,
        llvmwrap_ull)
_wrap_objobj2obj(LLVMStoreSizeOfType, LLVMTargetDataRef, LLVMTypeRef,
        llvmwrap_ull)
_wrap_objobj2obj(LLVMABISizeOfType, LLVMTargetDataRef, LLVMTypeRef,
        llvmwrap_ull)
_wrap_objobj2obj(LLVMABIAlignmentOfType, LLVMTargetDataRef, LLVMTypeRef,
        int)
_wrap_objobj2obj(LLVMCallFrameAlignmentOfType, LLVMTargetDataRef, LLVMTypeRef,
        int)
_wrap_objobj2obj(LLVMPreferredAlignmentOfType, LLVMTargetDataRef, LLVMTypeRef,
        int)
_wrap_objobj2obj(LLVMPreferredAlignmentOfGlobal, LLVMTargetDataRef,
        LLVMValueRef, int)
_wrap_objobjull2obj(LLVMElementAtOffset, LLVMTargetDataRef, LLVMTypeRef, int)
_wrap_objobjint2obj(LLVMOffsetOfElement, LLVMTargetDataRef, LLVMTypeRef,
        llvmwrap_ull)


/*===----------------------------------------------------------------------===*/
/* Engine Builder                                                             */
/*===----------------------------------------------------------------------===*/

_wrap_obj2obj(LLVMCreateEngineBuilder, LLVMModuleRef, LLVMEngineBuilderRef)
_wrap_obj2none(LLVMDisposeEngineBuilder, LLVMEngineBuilderRef)
_wrap_obj2none(LLVMEngineBuilderForceJIT, LLVMEngineBuilderRef)
_wrap_obj2none(LLVMEngineBuilderForceInterpreter, LLVMEngineBuilderRef)
_wrap_objint2none(LLVMEngineBuilderSetOptLevel, LLVMEngineBuilderRef)
_wrap_objstr2none(LLVMEngineBuilderSetMCPU, LLVMEngineBuilderRef)
_wrap_objstr2none(LLVMEngineBuilderSetMAttrs, LLVMEngineBuilderRef)

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

static PyObject *
_wLLVMEngineBuilderCreateTM(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj, *tm;
    if (!PyArg_ParseTuple(args, "OO", &obj, &tm))
        return NULL;

    const LLVMEngineBuilderRef objref = pycap_get<LLVMEngineBuilderRef>( obj );
    const LLVMTargetMachineRef tmref = pycap_get<LLVMTargetMachineRef>( tm );
    std::string outmsg;

    const LLVMExecutionEngineRef ee = LLVMEngineBuilderCreateTM(objref, tmref,
                                                                outmsg);

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

// Use EngineBuilder
//static PyObject *
//_wLLVMCreateExecutionEngine(PyObject *self, PyObject *args)
//{
//    LLVMPY_TRY
//    PyObject *obj;
//    int force_interpreter;
//    char *outmsg = 0;
//    int error;
//
//    if (!PyArg_ParseTuple(args, "Oi", &obj, &force_interpreter))
//        return NULL;
//
//    const LLVMModuleRef mod = pycap_get<LLVMModuleRef>( obj ) ;
//
//    LLVMExecutionEngineRef ee;
//    if (force_interpreter)
//        error = LLVMCreateInterpreterForModule(&ee, mod, &outmsg);
//    else
//        error = LLVMCreateJITCompilerForModule(&ee, mod, 1 /*fast*/, &outmsg);
//
//    PyObject *ret;
//    if (error) {
//        ret = PyUnicode_FromString(outmsg);
//        LLVMDisposeMessage(outmsg);
//    } else {
//        ret = pycap_new<LLVMExecutionEngineRef>(ee);
//    }
//
//    return ret;
//    LLVMPY_CATCH_ALL
//}

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

static PyObject *
_wLLVMGetPointerToGlobal(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj_ee;
    PyObject *obj_val;

    if (!PyArg_ParseTuple(args, "OO", &obj_ee, &obj_val))
        return NULL;

    const LLVMExecutionEngineRef ee = pycap_get<LLVMExecutionEngineRef>( obj_ee ) ;
    const LLVMValueRef val = pycap_get<LLVMValueRef>( obj_val ) ;

    return PyLong_FromVoidPtr(LLVMGetPointerToGlobal(ee, val));
    LLVMPY_CATCH_ALL
}

static PyObject *
_wLLVMAddGlobalMapping(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj_ee;
    PyObject *obj_val;
    PyObject *obj_long;
    void* address;

    if (!PyArg_ParseTuple(args, "OOO", &obj_ee, &obj_val, &obj_long))
        return NULL;

    address = PyLong_AsVoidPtr(obj_long);
    if (PyErr_Occurred()) return NULL;

    const LLVMExecutionEngineRef ee = pycap_get<LLVMExecutionEngineRef>( obj_ee );
    const LLVMValueRef val = pycap_get<LLVMValueRef>( obj_val );

    LLVMAddGlobalMapping(ee, val, address);

    Py_RETURN_NONE;

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

_wrap_obj2none(LLVMDisposeExecutionEngine, LLVMExecutionEngineRef)
_wrap_objint2none(LLVMExecutionEngineDisableLazyCompilation,
                  LLVMExecutionEngineRef)
_wrap_objobjlist2obj(LLVMRunFunction2, LLVMExecutionEngineRef,
    LLVMValueRef, LLVMGenericValueRef, LLVMGenericValueRef)
_wrap_obj2obj(LLVMGetExecutionEngineTargetData, LLVMExecutionEngineRef,
    LLVMTargetDataRef)
_wrap_obj2none(LLVMRunStaticConstructors, LLVMExecutionEngineRef)
_wrap_obj2none(LLVMRunStaticDestructors, LLVMExecutionEngineRef)
_wrap_objobj2none(LLVMFreeMachineCodeForFunction, LLVMExecutionEngineRef,
    LLVMValueRef)
_wrap_objobj2none(LLVMAddModule, LLVMExecutionEngineRef,
    LLVMModuleRef)


/*===----------------------------------------------------------------------===*/
/* Generic Value                                                              */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMCreateGenericValueOfInt(PyObject *self, PyObject *args)
{
    LLVMPY_TRY
    PyObject *obj1;
    unsigned PY_LONG_LONG n;
    int is_signed;
    LLVMGenericValueRef gv;

    if (!PyArg_ParseTuple(args, "OKi", &obj1, &n, &is_signed))
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
    unsigned PY_LONG_LONG n_;
    size_t n;

    if (!PyArg_ParseTuple(args, "K", &n_))
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
    unsigned PY_LONG_LONG val;

    if (!PyArg_ParseTuple(args, "Oi", &obj1, &is_signed))
        return NULL;

    LLVMGenericValueRef gv = pycap_get<LLVMGenericValueRef>(obj1);

    val = LLVMGenericValueToInt(gv, is_signed);
    return is_signed ?
        PyLong_FromLongLong((PY_LONG_LONG)val) :
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

_wrap_obj2none(LLVMDisposeGenericValue, LLVMGenericValueRef)


/*===----------------------------------------------------------------------===*/
/* Misc                                                                       */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMGetVersion(PyObject *self, PyObject *args)
{
    int major = LLVM_VERSION_MAJOR;
    int minor = LLVM_VERSION_MINOR;
    return Py_BuildValue("(i,i)", major, minor);
}

_wrap_objintlist2obj(LLVMGetIntrinsic, LLVMModuleRef, LLVMTypeRef,
    LLVMValueRef)

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

_wrap_obj2obj(LLVMInlineFunction, LLVMValueRef, int)

_wrap_none2str(LLVMDefaultTargetTriple)


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

#define _method( func )     { # func , ( PyCFunction )_w ## func , METH_VARARGS , NULL },
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
    _method( LLVMModuleGetOrInsertNamedMetaData )
    _method( LLVMModuleGetNamedMetaData )
    _method( LLVMCloneModule )

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
    _method( LLVMAddGlobalInAddressSpace )
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
    _method( LLVMGetFunctionFromInlineAsm )

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

    /* NamedMetaData */
    _method( LLVMNamedMetaDataGetName )
    _method( LLVMNamedMetaDataAddOperand )
    _method( LLVMEraseNamedMetaData )
    _method( LLVMDumpNamedMDToString )

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
    _method( LLVMInstructionEraseFromParent )

    /* Call Sites (Call or Invoke) */
    _method( LLVMSetInstructionCallConv )
    _method( LLVMGetInstructionCallConv )
    _method( LLVMIsTailCall )
    _method( LLVMSetTailCall )
    _method( LLVMAddInstrAttribute )
    _method( LLVMRemoveInstrAttribute )
    _method( LLVMSetInstrParamAlignment )
    _method( LLVMInstGetCalledFunction )
    _method( LLVMInstSetCalledFunction )

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
    _method( LLVMBuildInBoundsGEP )

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
#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
    _method( LLVMPassManagerBuilderSetLoopVectorize )
    _method( LLVMPassManagerBuilderGetLoopVectorize )
#endif // llvm-3.2

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
    _method( LLVMAddPass )
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

    /* Target Machine */
    _method( LLVMTargetMachineFromEngineBuilder )
    _method( LLVMDisposeTargetMachine )
    _method( LLVMCreateTargetMachine )
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
    _method( LLVMEngineBuilderCreateTM )

    /* Execution Engine */
// Use EngineBuilder instead
//    _method( LLVMCreateExecutionEngine )
    _method( LLVMDisposeExecutionEngine )
    _method( LLVMExecutionEngineDisableLazyCompilation )
    _method( LLVMRunFunction2 )
    _method( LLVMGetPointerToFunction )
    _method( LLVMGetPointerToGlobal )
    _method( LLVMAddGlobalMapping )
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

    /* Passes */
    _method( LLVMCreatePassByName )
    _method( LLVMDisposePass )
    _method( LLVMGetPassName )
    _method( LLVMPassDump )

    _method( LLVMCreateTargetLibraryInfo )

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
    _method( LLVMCreateTargetTransformInfo )
#endif

    /* Misc */
    _method( LLVMGetVersion )
    _method( LLVMGetIntrinsic )
    _method( LLVMLoadLibraryPermanently )
    _method( LLVMParseEnvOpts )
    _method( LLVMDefaultTargetTriple )
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
