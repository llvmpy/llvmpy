/**
 * These are some "extra" functions not available in the standard LLVM-C
 * bindings, but are required / good-to-have inorder to implement the
 * Python bindings.
 */

#ifndef LLVM_PY_EXTRA_H
#define LLVM_PY_EXTRA_H

#ifdef __cplusplus
extern "C" {
#endif

/** Dumps module contents to a string. See Module::print. Free the
    returned string with LLVMDisposeMessage, after use. */
char *LLVMDumpModuleToString(LLVMModuleRef M);

/** Dumps type to a string. See Type::print. Free the returned string with 
    LLVMDisposeMessage, after use. */
char *LLVMDumpTypeToString(LLVMTypeRef Ty);

/** Dumps value to a string. See Value::print. Free the returned string with
    LLVMDisposeMessage, after use. */
char *LLVMDumpValueToString(LLVMValueRef Val);

/* missing constant expressions */

#if 0 /* after LLVM 2.3! */
LLVMValueRef LLVMConstVICmp(LLVMIntPredicate Predicate,
                           LLVMValueRef LHSConstant, LLVMValueRef RHSConstant);
LLVMValueRef LLVMConstVFCmp(LLVMRealPredicate Predicate,
                           LLVMValueRef LHSConstant, LLVMValueRef RHSConstant);

/* missing instructions */

LLVMValueRef LLVMBuildVICmp(LLVMBuilderRef, LLVMIntPredicate Op,
                           LLVMValueRef LHS, LLVMValueRef RHS,
                           const char *Name);
LLVMValueRef LLVMBuildVFCmp(LLVMBuilderRef, LLVMRealPredicate Op,
                           LLVMValueRef LHS, LLVMValueRef RHS,
                           const char *Name);
#endif

LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef, LLVMValueRef *Values,
                                  unsigned NumValues);
LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef, LLVMValueRef V,
                                unsigned Index, const char *Name);

LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef B, int ID,
                              LLVMTypeRef *Types, unsigned Count);

LLVMModuleRef LLVMGetModuleFromBitcode(const char *BC, unsigned Len,
                                       char **OutMessage);
unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef M, unsigned *Len);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* LLVM_PY_EXTRA_H */

