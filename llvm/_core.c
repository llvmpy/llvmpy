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

/* our includes */
#include "wrap.h"
#include "extra.h"

/* LLVM includes */
#include "llvm-c/Analysis.h"
#include "llvm-c/Transforms/Scalar.h"
#include "llvm-c/ExecutionEngine.h"

/* libc includes */
#include <stdarg.h> /* for malloc(), free() */

/* Compatibility with Python 2.4: Py_ssize_t is not available. */
#ifndef PY_SSIZE_T_MAX
typedef int Py_ssize_t;
#endif


/*===----------------------------------------------------------------------===*/
/* Modules                                                                    */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMModuleCreateWithName(PyObject *self, PyObject *args)
{
    const char *s;
    LLVMModuleRef module;

    if (!PyArg_ParseTuple(args, "s", &s))
        return NULL;

    module = LLVMModuleCreateWithName(s);
    return ctor_LLVMModuleRef(module);
}

_wrap_obj2str(LLVMGetDataLayout, LLVMModuleRef)
_wrap_objstr2none(LLVMSetDataLayout, LLVMModuleRef)
_wrap_obj2str(LLVMGetTarget, LLVMModuleRef)
_wrap_objstr2none(LLVMSetTarget, LLVMModuleRef)
_wrap_objstrobj2obj(LLVMAddTypeName, LLVMModuleRef, LLVMTypeRef, int)
_wrap_objstr2none(LLVMDeleteTypeName, LLVMModuleRef)
_wrap_obj2none(LLVMDumpModule, LLVMModuleRef)
_wrap_obj2none(LLVMDisposeModule, LLVMModuleRef)
_wrap_dumper(LLVMDumpModuleToString, LLVMModuleRef)
_wrap_obj2obj(LLVMModuleGetPointerSize, LLVMModuleRef, int)
_wrap_objstrobj2obj(LLVMModuleGetOrInsertFunction, LLVMModuleRef, 
    LLVMTypeRef, LLVMValueRef)      

static PyObject *
_wLLVMVerifyModule(PyObject *self, PyObject *args)
{
    char *outmsg;
    PyObject *ret;
    LLVMModuleRef m;

    if (!(m = (LLVMModuleRef)get_object_arg(args)))
        return NULL;

    outmsg = 0;
    (void) LLVMVerifyModule(m, LLVMReturnStatusAction, &outmsg);

    if (outmsg) {
        ret = PyString_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    } else {
        ret = PyString_FromString("");
    }

    return ret;
}

typedef LLVMModuleRef (*asm_or_bc_fn_t)(const char *A, unsigned Len,
    char **OutMessage);

static PyObject *
_get_asm_or_bc(asm_or_bc_fn_t fn, PyObject *self, PyObject *args)
{
    PyObject *obj, *ret;
    Py_ssize_t len;
    char *start, *outmsg;
    LLVMModuleRef m;

    if (!PyArg_ParseTuple(args, "O", &obj))
        return NULL;

    start = PyString_AsString(obj);
    len = PyString_Size(obj);

    outmsg = 0;
    m = fn(start, len, &outmsg);
    if (!m) {
        if (outmsg) {
            ret = PyString_FromString(outmsg);
            LLVMDisposeMessage(outmsg);
            return ret;
        } else {
            Py_RETURN_NONE;
        }
    }

    return ctor_LLVMModuleRef(m);
}

static PyObject *
_wLLVMGetModuleFromAssembly(PyObject *self, PyObject *args)
{
    return _get_asm_or_bc(LLVMGetModuleFromAssembly, self, args);
}

static PyObject *
_wLLVMGetModuleFromBitcode(PyObject *self, PyObject *args)
{
    return _get_asm_or_bc(LLVMGetModuleFromBitcode, self, args);
}

static PyObject *
_wLLVMGetBitcodeFromModule(PyObject *self, PyObject *args)
{
    PyObject *ret;
    unsigned len;
    unsigned char *bytes;
    LLVMModuleRef m;

    if (!(m = (LLVMModuleRef)get_object_arg(args)))
        return NULL;

    if (!(bytes = LLVMGetBitcodeFromModule(m, &len)))
        Py_RETURN_NONE;

    ret = PyString_FromStringAndSize((char *)bytes, (Py_ssize_t)len);
    LLVMDisposeMessage((char *)bytes);
    return ret;
}

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
    LLVMTypeRef type, *param_types;
    unsigned param_count;
    PyObject *list;

    /* get the function object ptr */
    if (!(type = (LLVMTypeRef)get_object_arg(args)))
        return NULL;

    /* get param count */
    param_count = cntfunc(type);

    /* alloc enough space for all of them */
    if (!(param_types = (LLVMTypeRef *)malloc(sizeof(LLVMTypeRef) * param_count)))
        return PyErr_NoMemory();

    /* call LLVM func */
    arrfunc(type, param_types);

    /* create a list from the array */
    list = make_list_from_LLVMTypeRef_array(param_types, param_count);

    /* free temp storage */
    free(param_types);

    return list;
}

static PyObject *
_wLLVMGetFunctionTypeParams(PyObject *self, PyObject *args)
{
    return obj2arr(self, args, LLVMCountParamTypes, LLVMGetParamTypes);
}

/*===-- Struct types -----------------------------------------------------===*/

_wrap_listint2obj(LLVMStructType, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMCountStructElementTypes, LLVMTypeRef, int)

static PyObject *
_wLLVMGetStructElementTypes(PyObject *self, PyObject *args)
{
    return obj2arr(self, args, LLVMCountStructElementTypes, LLVMGetStructElementTypes);
}

_wrap_obj2obj(LLVMIsPackedStruct, LLVMTypeRef, int)

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
_wrap_none2obj(LLVMOpaqueType, LLVMTypeRef)

/*===-- Type handles -----------------------------------------------------===*/

_wrap_obj2obj(LLVMCreateTypeHandle, LLVMTypeRef, LLVMTypeHandleRef)
_wrap_objobj2none(LLVMRefineType, LLVMTypeRef, LLVMTypeRef)
_wrap_obj2obj(LLVMResolveTypeHandle, LLVMTypeHandleRef, LLVMTypeRef)
_wrap_obj2none(LLVMDisposeTypeHandle, LLVMTypeHandleRef)


/*===----------------------------------------------------------------------===*/
/* Values                                                                     */
/*===----------------------------------------------------------------------===*/

/* Operations on all values */

_wrap_obj2obj(LLVMTypeOf, LLVMValueRef, LLVMTypeRef)
_wrap_obj2str(LLVMGetValueName, LLVMValueRef)
_wrap_objstr2none(LLVMSetValueName, LLVMValueRef)
_wrap_obj2none(LLVMDumpValue, LLVMValueRef)
_wrap_dumper(LLVMDumpValueToString, LLVMValueRef)

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
    PyObject *obj;
    unsigned long long n;
    int sign_extend;
    LLVMTypeRef ty;
    LLVMValueRef val;
    
    if (!PyArg_ParseTuple(args, "OKi", &obj, &n, &sign_extend))
        return NULL;
    
    ty = (LLVMTypeRef)(PyCObject_AsVoidPtr(obj));
    val = LLVMConstInt(ty, n, sign_extend);
    return ctor_LLVMValueRef(val);
}

static PyObject *
_wLLVMConstReal(PyObject *self, PyObject *args)
{
    PyObject *obj;
    double d;
    LLVMTypeRef ty;
    LLVMValueRef val;
    
    if (!PyArg_ParseTuple(args, "Od", &obj, &d))
        return NULL;
    
    ty = (LLVMTypeRef)(PyCObject_AsVoidPtr(obj));
    val = LLVMConstReal(ty, d);
    return ctor_LLVMValueRef(val);
}

_wrap_objstr2obj(LLVMConstRealOfString, LLVMTypeRef, LLVMValueRef)

/* Operations on composite constants */

static PyObject *
_wLLVMConstString(PyObject *self, PyObject *args)
{
    const char *s;
    int dont_null_terminate;
    LLVMValueRef val;
    
    if (!PyArg_ParseTuple(args, "si", &s, &dont_null_terminate))
        return NULL;
    
    val = LLVMConstString(s, strlen(s), dont_null_terminate);
    return ctor_LLVMValueRef(val);
}

_wrap_objlist2obj(LLVMConstArray, LLVMTypeRef, LLVMValueRef, LLVMValueRef)
_wrap_listint2obj(LLVMConstStruct, LLVMValueRef, LLVMValueRef)
_wrap_list2obj(LLVMConstVector, LLVMValueRef, LLVMValueRef)

/* Constant expressions */

_wrap_obj2obj(LLVMSizeOf, LLVMTypeRef, LLVMValueRef)
_wrap_obj2obj(LLVMConstNeg, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMConstNot, LLVMValueRef, LLVMValueRef)

_wrap_objobj2obj(LLVMConstAdd, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSub, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstMul, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstUDiv, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSDiv, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFDiv, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstURem, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstSRem, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstFRem, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstAnd, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstOr, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobj2obj(LLVMConstXor, LLVMValueRef, LLVMValueRef, LLVMValueRef)

_wrap_intobjobj2obj(LLVMConstICmp, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_intobjobj2obj(LLVMConstFCmp, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_intobjobj2obj(LLVMConstVICmp, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_intobjobj2obj(LLVMConstVFCmp, LLVMValueRef, LLVMValueRef, LLVMValueRef)

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
_wrap_objint2none(LLVMSetLinkage, LLVMValueRef) 
_wrap_obj2str(LLVMGetSection, LLVMValueRef)
_wrap_objstr2none(LLVMSetSection, LLVMValueRef)
_wrap_obj2obj(LLVMGetVisibility, LLVMValueRef, int)
_wrap_objint2none(LLVMSetVisibility, LLVMValueRef)
_wrap_obj2obj(LLVMGetAlignment, LLVMValueRef, int)
_wrap_objint2none(LLVMSetAlignment, LLVMValueRef)

/*===-- Global Variables -------------------------------------------------===*/

_wrap_objobjstr2obj(LLVMAddGlobal, LLVMModuleRef, LLVMTypeRef, LLVMValueRef)
_wrap_objstr2obj(LLVMGetNamedGlobal, LLVMModuleRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetFirstGlobal, LLVMModuleRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetNextGlobal, LLVMValueRef, LLVMValueRef)
_wrap_obj2none(LLVMDeleteGlobal, LLVMValueRef)
_wrap_obj2obj(LLVMHasInitializer, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetInitializer, LLVMValueRef, LLVMValueRef)
_wrap_objobj2none(LLVMSetInitializer, LLVMValueRef, LLVMValueRef)
_wrap_objint2none(LLVMSetThreadLocal, LLVMValueRef)
_wrap_objint2none(LLVMSetGlobalConstant, LLVMValueRef)
_wrap_obj2obj(LLVMIsThreadLocal, LLVMValueRef, int)
_wrap_obj2obj(LLVMIsGlobalConstant, LLVMValueRef, int)

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
_wrap_obj2none(LLVMViewFunctionCFG, LLVMValueRef)
_wrap_obj2none(LLVMViewFunctionCFGOnly, LLVMValueRef)

static PyObject *
_wLLVMVerifyFunction(PyObject *self, PyObject *args)
{
    LLVMValueRef fn;

    if (!(fn = (LLVMValueRef)get_object_arg(args)))
        return NULL;

    return ctor_int(LLVMVerifyFunction(fn, LLVMReturnStatusAction));
}


/*===-- Arguments --------------------------------------------------------===*/

_wrap_obj2obj(LLVMCountParams, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetFirstParam, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetNextParam, LLVMValueRef, LLVMValueRef)
_wrap_obj2obj(LLVMGetParamParent, LLVMValueRef, LLVMValueRef)
_wrap_objint2none(LLVMAddAttribute, LLVMValueRef)
_wrap_objint2none(LLVMRemoveAttribute, LLVMValueRef)
_wrap_objint2none(LLVMSetParamAlignment, LLVMValueRef)

/*===-- Basic Blocks -----------------------------------------------------===*/

_wrap_obj2obj(LLVMGetBasicBlockParent, LLVMBasicBlockRef, LLVMValueRef)
_wrap_obj2obj(LLVMCountBasicBlocks, LLVMValueRef, int)
_wrap_obj2obj(LLVMGetFirstBasicBlock, LLVMValueRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMGetNextBasicBlock, LLVMBasicBlockRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMGetEntryBasicBlock, LLVMValueRef, LLVMBasicBlockRef)
_wrap_objstr2obj(LLVMAppendBasicBlock, LLVMValueRef, LLVMBasicBlockRef)
_wrap_objstr2obj(LLVMInsertBasicBlock, LLVMBasicBlockRef, LLVMBasicBlockRef)
_wrap_obj2none(LLVMDeleteBasicBlock, LLVMBasicBlockRef)

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
_wrap_obj2obj(LLVMInstIsTrapping,     LLVMValueRef, int)
_wrap_obj2obj(LLVMInstGetOpcode,      LLVMValueRef, int)
_wrap_obj2str(LLVMInstGetOpcodeName,  LLVMValueRef)


/*===-- Call Sites (Call or Invoke) --------------------------------------===*/

_wrap_objint2none(LLVMSetInstructionCallConv, LLVMValueRef)
_wrap_obj2obj(LLVMGetInstructionCallConv, LLVMValueRef, int)
_wrap_objintint2none(LLVMAddInstrAttribute, LLVMValueRef)
_wrap_objintint2none(LLVMRemoveInstrAttribute, LLVMValueRef)
_wrap_objintint2none(LLVMSetInstrParamAlignment, LLVMValueRef)

/*===-- PHI Nodes --------------------------------------------------------===*/

static void LLVMAddIncoming1(LLVMValueRef PhiNode, LLVMValueRef IncomingValue, LLVMBasicBlockRef IncomingBlock)
{
    LLVMAddIncoming(PhiNode, &IncomingValue, &IncomingBlock, 1);
}

_wrap_objobjobj2none(LLVMAddIncoming1, LLVMValueRef, LLVMValueRef, LLVMBasicBlockRef)
_wrap_obj2obj(LLVMCountIncoming,       LLVMValueRef, int)
_wrap_objint2obj(LLVMGetIncomingValue, LLVMValueRef, LLVMValueRef)
_wrap_objint2obj(LLVMGetIncomingBlock, LLVMValueRef, LLVMBasicBlockRef)

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
    PyObject *obj1, *obj2, *obj3, *obj4, *obj5;
    const char *name;
    LLVMBuilderRef builder;
    LLVMValueRef func;
    LLVMValueRef *fnargs;
    unsigned fnarg_count;
    LLVMBasicBlockRef then_blk, catch_blk;
    LLVMValueRef inst;

    if (!PyArg_ParseTuple(args, "OOOOOs", &obj1, &obj2, &obj3, &obj4, &obj5, &name))
        return NULL;

    builder = (LLVMBuilderRef)(PyCObject_AsVoidPtr(obj1));
    func    = (LLVMValueRef)(PyCObject_AsVoidPtr(obj2));
    fnarg_count = (unsigned) PyList_Size(obj3);
    fnargs = (LLVMValueRef *)make_array_from_list(obj3, fnarg_count);
    if (!fnargs)
        return PyErr_NoMemory();
    then_blk = (LLVMBasicBlockRef)(PyCObject_AsVoidPtr(obj4));
    catch_blk = (LLVMBasicBlockRef)(PyCObject_AsVoidPtr(obj5));

    inst = LLVMBuildInvoke(builder, func, fnargs, fnarg_count, then_blk, catch_blk, name);

    free(fnargs);

    return ctor_LLVMValueRef(inst);
}

_wrap_obj2obj(LLVMBuildUnwind, LLVMBuilderRef, LLVMValueRef)
_wrap_obj2obj(LLVMBuildUnreachable, LLVMBuilderRef, LLVMValueRef)

/* Add a case to the switch instruction */

_wrap_objobjobj2none(LLVMAddCase, LLVMValueRef, LLVMValueRef, LLVMBasicBlockRef)

/* Arithmetic */

_wrap_objobjobjstr2obj(LLVMBuildAdd, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildSub, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildMul, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
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

_wrap_objintobjobjstr2obj(LLVMBuildICmp, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objintobjobjstr2obj(LLVMBuildFCmp, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objintobjobjstr2obj(LLVMBuildVICmp, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objintobjobjstr2obj(LLVMBuildVFCmp, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)

/* Miscellaneous instructions */

_wrap_objobjintstr2obj(LLVMBuildGetResult, LLVMBuilderRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjstr2obj(LLVMBuildPhi, LLVMBuilderRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjliststr2obj(LLVMBuildCall, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjobjstr2obj(LLVMBuildSelect, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildVAArg, LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, LLVMValueRef)
_wrap_objobjobjstr2obj(LLVMBuildExtractElement, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjobjstr2obj(LLVMBuildInsertElement, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)
_wrap_objobjobjobjstr2obj(LLVMBuildShuffleVector, LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, LLVMValueRef)


/*===----------------------------------------------------------------------===*/
/* Modules Providers                                                          */
/*===----------------------------------------------------------------------===*/

_wrap_obj2obj(LLVMCreateModuleProviderForExistingModule, LLVMModuleRef, LLVMModuleProviderRef)
_wrap_obj2none(LLVMDisposeModuleProvider, LLVMModuleProviderRef)


/*===----------------------------------------------------------------------===*/
/* Memory Buffer                                                              */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMCreateMemoryBufferWithContentsOfFile(PyObject *self, PyObject *args)
{
    const char *path;
    LLVMMemoryBufferRef ref;
    char *outmsg;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    if (!LLVMCreateMemoryBufferWithContentsOfFile(path, &ref, &outmsg)) {
        ret = ctor_LLVMMemoryBufferRef(ref);
    } else {
        ret = PyString_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    }

    return ret;
}

static PyObject *
_wLLVMCreateMemoryBufferWithSTDIN(PyObject *self, PyObject *args)
{
    LLVMMemoryBufferRef ref;
    char *outmsg;
    PyObject *ret;

    if (!LLVMCreateMemoryBufferWithSTDIN(&ref, &outmsg)) {
        ret = ctor_LLVMMemoryBufferRef(ref);
    } else {
        ret = PyString_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    }

    return ret;
}

_wrap_obj2none(LLVMDisposeMemoryBuffer, LLVMMemoryBufferRef)


/*===----------------------------------------------------------------------===*/
/* Pass Manager                                                               */
/*===----------------------------------------------------------------------===*/

_wrap_none2obj(LLVMCreatePassManager, LLVMPassManagerRef)
_wrap_obj2obj(LLVMCreateFunctionPassManager, LLVMModuleProviderRef, LLVMPassManagerRef)
_wrap_objobj2obj(LLVMRunPassManager, LLVMPassManagerRef, LLVMModuleRef, int)
_wrap_obj2obj(LLVMInitializeFunctionPassManager, LLVMPassManagerRef, int)
_wrap_objobj2obj(LLVMRunFunctionPassManager, LLVMPassManagerRef, LLVMValueRef, int)
_wrap_obj2obj(LLVMFinalizeFunctionPassManager, LLVMPassManagerRef, int)
_wrap_obj2none(LLVMDisposePassManager, LLVMPassManagerRef)


/*===----------------------------------------------------------------------===*/
/* Passes                                                                     */
/*===----------------------------------------------------------------------===*/

#define _wrap_pass(P)   \
_wrap_obj2none( LLVMAdd ## P ## Pass, LLVMPassManagerRef)

_wrap_pass( AggressiveDCE )
_wrap_pass( ArgumentPromotion )
_wrap_pass( BlockPlacement )
_wrap_pass( BreakCriticalEdges )
_wrap_pass( CodeGenPrepare )
_wrap_pass( CondPropagation )
_wrap_pass( ConstantMerge )
_wrap_pass( ConstantPropagation )
_wrap_pass( DeadCodeElimination )
_wrap_pass( DeadArgElimination )
_wrap_pass( DeadTypeElimination )
_wrap_pass( DeadInstElimination )
_wrap_pass( DeadStoreElimination )
/* _wrap_pass( GCSE ): removed in LLVM 2.4. */
_wrap_pass( GlobalDCE )
_wrap_pass( GlobalOptimizer )
_wrap_pass( GVN )
_wrap_pass( GVNPRE )
_wrap_pass( IndMemRem )
_wrap_pass( IndVarSimplify )
_wrap_pass( FunctionInlining )
_wrap_pass( BlockProfiler )
_wrap_pass( EdgeProfiler )
_wrap_pass( FunctionProfiler )
_wrap_pass( NullProfilerRS )
_wrap_pass( RSProfiling )
_wrap_pass( InstructionCombining )
_wrap_pass( Internalize )
_wrap_pass( IPConstantPropagation )
_wrap_pass( IPSCCP )
_wrap_pass( JumpThreading )
_wrap_pass( LCSSA )
_wrap_pass( LICM )
_wrap_pass( LoopDeletion )
_wrap_pass( LoopExtractor )
_wrap_pass( SingleLoopExtractor )
_wrap_pass( LoopIndexSplit )
_wrap_pass( LoopStrengthReduce )
_wrap_pass( LoopRotate )
_wrap_pass( LoopUnroll )
_wrap_pass( LoopUnswitch )
_wrap_pass( LoopSimplify )
_wrap_pass( LowerAllocations )
_wrap_pass( LowerInvoke )
_wrap_pass( LowerSetJmp )
_wrap_pass( LowerSwitch )
_wrap_pass( PromoteMemoryToRegister )
_wrap_pass( MemCpyOpt )
_wrap_pass( UnifyFunctionExitNodes )
_wrap_pass( PredicateSimplifier )
_wrap_pass( PruneEH )
_wrap_pass( RaiseAllocations )
_wrap_pass( Reassociate )
_wrap_pass( DemoteRegisterToMemory )
_wrap_pass( ScalarReplAggregates )
_wrap_pass( SCCP )
_wrap_pass( SimplifyLibCalls )
_wrap_pass( CFGSimplification )
_wrap_pass( StripSymbols )
_wrap_pass( StripDeadPrototypes )
_wrap_pass( StructRetPromotion )
_wrap_pass( TailCallElimination )
_wrap_pass( TailDuplication )

/*===----------------------------------------------------------------------===*/
/* Target Data                                                                */
/*===----------------------------------------------------------------------===*/

_wrap_str2obj(LLVMCreateTargetData, LLVMTargetDataRef)
_wrap_obj2none(LLVMDisposeTargetData, LLVMTargetDataRef)

static PyObject *
_wLLVMTargetDataAsString(PyObject *self, PyObject *args)
{
    LLVMTargetDataRef td;
    char *tdrep = 0;
    PyObject *ret;

    if (!(td = (LLVMTargetDataRef)get_object_arg(args)))
        return NULL;

    tdrep = LLVMCopyStringRepOfTargetData(td);
    ret = PyString_FromString(tdrep);
    LLVMDisposeMessage(tdrep);
    return ret;
}

_wrap_objobj2none(LLVMAddTargetData, LLVMTargetDataRef, LLVMPassManagerRef)


/*===----------------------------------------------------------------------===*/
/* Execution Engine                                                           */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMCreateExecutionEngine(PyObject *self, PyObject *args)
{
    LLVMModuleProviderRef mp;
    PyObject *obj;
    int force_interpreter;
    LLVMExecutionEngineRef ee;
    char *outmsg;
    PyObject *ret;
    int error;

    if (!PyArg_ParseTuple(args, "Oi", &obj, &force_interpreter))
        return NULL;

    mp = (LLVMModuleProviderRef) PyCObject_AsVoidPtr(obj);

    if (force_interpreter)
        error = LLVMCreateInterpreter(&ee, mp, &outmsg);
    else
        error = LLVMCreateJITCompiler(&ee, mp, 1 /*fast*/, &outmsg);

    if (error) {
        ret = PyString_FromString(outmsg);
        LLVMDisposeMessage(outmsg);
    } else {
        ret = ctor_LLVMExecutionEngineRef(ee);
    }

    return ret;
}

/* the args should have been ptr, num */
LLVMGenericValueRef LLVMRunFunction2(LLVMExecutionEngineRef EE,
    LLVMValueRef F, LLVMGenericValueRef *Args, unsigned NumArgs)
{
    return LLVMRunFunction(EE, F, NumArgs, Args);
}

_wrap_obj2none(LLVMDisposeExecutionEngine, LLVMExecutionEngineRef)
_wrap_objobjlist2obj(LLVMRunFunction2, LLVMExecutionEngineRef,
    LLVMValueRef, LLVMGenericValueRef, LLVMGenericValueRef)
_wrap_obj2obj(LLVMGetExecutionEngineTargetData, LLVMExecutionEngineRef,
    LLVMTargetDataRef)
_wrap_obj2none(LLVMRunStaticConstructors, LLVMExecutionEngineRef)
_wrap_obj2none(LLVMRunStaticDestructors, LLVMExecutionEngineRef)
_wrap_objobj2none(LLVMFreeMachineCodeForFunction, LLVMExecutionEngineRef,
    LLVMValueRef)
_wrap_objobj2none(LLVMAddModuleProvider, LLVMExecutionEngineRef,
    LLVMModuleProviderRef)


/*===----------------------------------------------------------------------===*/
/* Generic Value                                                              */
/*===----------------------------------------------------------------------===*/

static PyObject *
_wLLVMCreateGenericValueOfInt(PyObject *self, PyObject *args)
{
    PyObject *obj1;
    LLVMTypeRef ty;
    unsigned long long n;
    int is_signed;
    LLVMGenericValueRef gv;

    if (!PyArg_ParseTuple(args, "OLi", &obj1, &n, &is_signed))
        return NULL;

    ty = (LLVMTypeRef) PyCObject_AsVoidPtr(obj1);

    gv = LLVMCreateGenericValueOfInt(ty, n, is_signed);
    return ctor_LLVMGenericValueRef(gv);
}

static PyObject *
_wLLVMCreateGenericValueOfFloat(PyObject *self, PyObject *args)
{
    PyObject *obj1;
    LLVMTypeRef ty;
    double d;
    LLVMGenericValueRef gv;

    if (!PyArg_ParseTuple(args, "Od", &obj1, &d))
        return NULL;

    ty = (LLVMTypeRef) PyCObject_AsVoidPtr(obj1);

    gv = LLVMCreateGenericValueOfFloat(ty, d);
    return ctor_LLVMGenericValueRef(gv);
}

static PyObject *
_wLLVMGenericValueToInt(PyObject *self, PyObject *args)
{
    PyObject *obj1;
    int is_signed;
    LLVMGenericValueRef gv;
    unsigned long long val;

    if (!PyArg_ParseTuple(args, "Oi", &obj1, &is_signed))
        return NULL;

    gv = (LLVMGenericValueRef) PyCObject_AsVoidPtr(obj1);

    val = LLVMGenericValueToInt(gv, is_signed);
    return is_signed ?
        PyLong_FromLongLong((long long)val) :
        PyLong_FromUnsignedLongLong(val);
}

static PyObject *
_wLLVMGenericValueToFloat(PyObject *self, PyObject *args)
{
    PyObject *obj1, *obj2;
    LLVMTypeRef ty;
    LLVMGenericValueRef gv;
    double val;

    if (!PyArg_ParseTuple(args, "OO", &obj1, &obj2))
        return NULL;

    ty = (LLVMTypeRef) PyCObject_AsVoidPtr(obj1);
    gv = (LLVMGenericValueRef) PyCObject_AsVoidPtr(obj2);

    val = LLVMGenericValueToFloat(ty, gv);
    return PyFloat_FromDouble(val);
}

_wrap_obj2none(LLVMDisposeGenericValue, LLVMGenericValueRef)


/*===----------------------------------------------------------------------===*/
/* Misc                                                                       */
/*===----------------------------------------------------------------------===*/

_wrap_objintlist2obj(LLVMGetIntrinsic, LLVMModuleRef, LLVMTypeRef,
    LLVMValueRef)

static PyObject *
_wLLVMLoadLibraryPermanently(PyObject *self, PyObject *args)
{
    const char *filename;
    char *outmsg;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s", &filename))
        return NULL;

    outmsg = 0;
    if (!LLVMLoadLibraryPermanently(filename, &outmsg)) {
        if (outmsg) {
            ret = PyString_FromString(outmsg);
            LLVMDisposeMessage(outmsg);
            return ret;
        }
    }

    /* note: success => None, failure => string with error message */
    Py_RETURN_NONE;
}


/*===----------------------------------------------------------------------===*/
/* Python member method table                                                 */
/*===----------------------------------------------------------------------===*/

#define _method( func )     { # func , _w ## func , METH_VARARGS },
#define _pass( P )          _method( LLVMAdd ## P ## Pass )

static PyMethodDef core_methods[] = {

    /* Modules */
    _method( LLVMModuleCreateWithName )    
    _method( LLVMGetDataLayout )    
    _method( LLVMSetDataLayout )    
    _method( LLVMGetTarget )    
    _method( LLVMSetTarget )    
    _method( LLVMAddTypeName )    
    _method( LLVMDeleteTypeName )    
    _method( LLVMDumpModule )
    _method( LLVMDisposeModule )
    _method( LLVMDumpModuleToString )
    _method( LLVMVerifyModule )
    _method( LLVMGetModuleFromAssembly )
    _method( LLVMGetModuleFromBitcode )
    _method( LLVMGetBitcodeFromModule )
    _method( LLVMModuleGetPointerSize )
    _method( LLVMModuleGetOrInsertFunction )

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
    _method( LLVMCountStructElementTypes )    
    _method( LLVMGetStructElementTypes )    
    _method( LLVMIsPackedStruct )    

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
    _method( LLVMOpaqueType )    

    /* Type handles */
    _method( LLVMCreateTypeHandle )    
    _method( LLVMRefineType )    
    _method( LLVMResolveTypeHandle )    
    _method( LLVMDisposeTypeHandle )

    /* Values */

    /* Operations on all values */
    _method( LLVMTypeOf )    
    _method( LLVMGetValueName )    
    _method( LLVMSetValueName )    
    _method( LLVMDumpValue )    
    _method( LLVMDumpValueToString )

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

    /* Operations on composite constants */
    _method( LLVMConstString )    
    _method( LLVMConstArray )    
    _method( LLVMConstStruct )    
    _method( LLVMConstVector )    

    /* Constant expressions */
    _method( LLVMSizeOf )    
    _method( LLVMConstNeg )    
    _method( LLVMConstNot )    
    _method( LLVMConstAdd )    
    _method( LLVMConstSub )    
    _method( LLVMConstMul )    
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
    _method( LLVMConstVICmp )
    _method( LLVMConstVFCmp )
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
    _method( LLVMSetGlobalConstant )    
    _method( LLVMIsThreadLocal )    
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
    _method( LLVMVerifyFunction )
    _method( LLVMViewFunctionCFG )
    _method( LLVMViewFunctionCFGOnly )

    /* Arguments */
    _method( LLVMCountParams )    
    _method( LLVMGetFirstParam )    
    _method( LLVMGetNextParam )    
    _method( LLVMGetParamParent )    
    _method( LLVMAddAttribute )
    _method( LLVMRemoveAttribute )
    _method( LLVMSetParamAlignment )    

    /* Basic Blocks */
    _method( LLVMGetBasicBlockParent )    
    _method( LLVMCountBasicBlocks )    
    _method( LLVMGetFirstBasicBlock )
    _method( LLVMGetNextBasicBlock )
    _method( LLVMGetEntryBasicBlock )    
    _method( LLVMAppendBasicBlock )    
    _method( LLVMInsertBasicBlock )    
    _method( LLVMDeleteBasicBlock )    

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
    _method( LLVMInstIsTrapping )
    _method( LLVMInstGetOpcode )
    _method( LLVMInstGetOpcodeName )

    /* Call Sites (Call or Invoke) */
    _method( LLVMSetInstructionCallConv )    
    _method( LLVMGetInstructionCallConv )    
    _method( LLVMAddInstrAttribute )    
    _method( LLVMRemoveInstrAttribute )    
    _method( LLVMSetInstrParamAlignment )    

    /* PHI Nodes */
    _method( LLVMAddIncoming1 )    
    _method( LLVMCountIncoming )    
    _method( LLVMGetIncomingValue )    
    _method( LLVMGetIncomingBlock )    

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
    _method( LLVMBuildUnwind )    
    _method( LLVMBuildUnreachable )    

    /* Add a case to the switch instruction */
    _method( LLVMAddCase )    

    /* Arithmetic */
    _method( LLVMBuildAdd )    
    _method( LLVMBuildSub )    
    _method( LLVMBuildMul )    
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
    _method( LLVMBuildVICmp )    
    _method( LLVMBuildVFCmp )    

    /* Miscellaneous instructions */
    _method( LLVMBuildGetResult )    
    _method( LLVMBuildPhi )    
    _method( LLVMBuildCall )    
    _method( LLVMBuildSelect )    
    _method( LLVMBuildVAArg )    
    _method( LLVMBuildExtractElement )    
    _method( LLVMBuildInsertElement )    
    _method( LLVMBuildShuffleVector )    

    /* Modules Providers */
    _method( LLVMCreateModuleProviderForExistingModule )    
    _method( LLVMDisposeModuleProvider )

    /* Memory Buffer */
    _method( LLVMCreateMemoryBufferWithContentsOfFile )
    _method( LLVMCreateMemoryBufferWithSTDIN )
    _method( LLVMDisposeMemoryBuffer )

    /* Pass Manager */
    _method( LLVMCreatePassManager )    
    _method( LLVMCreateFunctionPassManager )    
    _method( LLVMRunPassManager )    
    _method( LLVMInitializeFunctionPassManager )    
    _method( LLVMRunFunctionPassManager )    
    _method( LLVMFinalizeFunctionPassManager )    
    _method( LLVMDisposePassManager )

    /* Passes */
    _pass( AggressiveDCE )
    _pass( ArgumentPromotion )
    _pass( BlockPlacement )
    _pass( BreakCriticalEdges )
    _pass( CodeGenPrepare )
    _pass( CondPropagation )
    _pass( ConstantMerge )
    _pass( ConstantPropagation )
    _pass( DeadCodeElimination )
    _pass( DeadArgElimination )
    _pass( DeadTypeElimination )
    _pass( DeadInstElimination )
    _pass( DeadStoreElimination )
    /* _pass( GCSE ): removed in LLVM 2.4. */
    _pass( GlobalDCE )
    _pass( GlobalOptimizer )
    _pass( GVN )
    _pass( GVNPRE )
    _pass( IndMemRem )
    _pass( IndVarSimplify )
    _pass( FunctionInlining )
    _pass( BlockProfiler )
    _pass( EdgeProfiler )
    _pass( FunctionProfiler )
    _pass( NullProfilerRS )
    _pass( RSProfiling )
    _pass( InstructionCombining )
    _pass( Internalize )
    _pass( IPConstantPropagation )
    _pass( IPSCCP )
    _pass( JumpThreading )
    _pass( LCSSA )
    _pass( LICM )
    _pass( LoopDeletion )
    _pass( LoopExtractor )
    _pass( SingleLoopExtractor )
    _pass( LoopIndexSplit )
    _pass( LoopStrengthReduce )
    _pass( LoopRotate )
    _pass( LoopUnroll )
    _pass( LoopUnswitch )
    _pass( LoopSimplify )
    _pass( LowerAllocations )
    _pass( LowerInvoke )
    _pass( LowerSetJmp )
    _pass( LowerSwitch )
    _pass( PromoteMemoryToRegister )
    _pass( MemCpyOpt )
    _pass( UnifyFunctionExitNodes )
    _pass( PredicateSimplifier )
    _pass( PruneEH )
    _pass( RaiseAllocations )
    _pass( Reassociate )
    _pass( DemoteRegisterToMemory )
    _pass( ScalarReplAggregates )
    _pass( SCCP )
    _pass( SimplifyLibCalls )
    _pass( CFGSimplification )
    _pass( StripSymbols )
    _pass( StripDeadPrototypes )
    _pass( StructRetPromotion )
    _pass( TailCallElimination )
    _pass( TailDuplication )

    /* Target Data */
    _method( LLVMCreateTargetData )
    _method( LLVMDisposeTargetData )
    _method( LLVMTargetDataAsString )
    _method( LLVMAddTargetData )

    /* Execution Engine */
    _method( LLVMCreateExecutionEngine )
    _method( LLVMDisposeExecutionEngine )
    _method( LLVMRunFunction2 )
    _method( LLVMGetExecutionEngineTargetData )
    _method( LLVMRunStaticConstructors )
    _method( LLVMRunStaticDestructors )
    _method( LLVMFreeMachineCodeForFunction )
    _method( LLVMAddModuleProvider )

    /* Generic Value */
    _method( LLVMCreateGenericValueOfInt )
    _method( LLVMCreateGenericValueOfFloat )
    _method( LLVMGenericValueToInt )
    _method( LLVMGenericValueToFloat )
    _method( LLVMDisposeGenericValue )

    /* Misc */
    _method( LLVMGetIntrinsic )
    _method( LLVMLoadLibraryPermanently )

    { NULL }
};

PyMODINIT_FUNC
init_core(void)
{
    Py_InitModule("_core", core_methods);
}
