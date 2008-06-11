/**
 * These are some "extra" functions not available in the standard LLVM-C
 * bindings, but are required / good-to-have inorder to implement the
 * Python bindings.
 */

#include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/Constants.h"
#include "llvm/DerivedTypes.h"
#include "llvm/GlobalVariable.h"
#include "llvm/TypeSymbolTable.h"
#include "llvm/ModuleProvider.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/CallSite.h"
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <sstream>

#include "llvm-c/Core.h"
#include "llvm/Analysis/Verifier.h"
#include "extra.h"

using namespace llvm;

char *LLVMDumpModuleToString(LLVMModuleRef M) {
  std::ostringstream buf;
  unwrap(M)->print(buf);
  return strdup(buf.str().c_str());
}

char *LLVMDumpTypeToString(LLVMTypeRef Ty) {
  std::ostringstream buf;
  unwrap(Ty)->print(buf);
  return strdup(buf.str().c_str());
}

char *LLVMDumpValueToString(LLVMValueRef Val) {
  std::ostringstream buf;
  unwrap(Val)->print(buf);
  return strdup(buf.str().c_str());
}

LLVMValueRef LLVMConstVICmp(LLVMIntPredicate Predicate,
                           LLVMValueRef LHSConstant, LLVMValueRef RHSConstant) {
  return wrap(ConstantExpr::getVICmp(Predicate,
                                    unwrap<Constant>(LHSConstant),
                                    unwrap<Constant>(RHSConstant)));
}

LLVMValueRef LLVMConstVFCmp(LLVMRealPredicate Predicate,
                           LLVMValueRef LHSConstant, LLVMValueRef RHSConstant) {
  return wrap(ConstantExpr::getVFCmp(Predicate,
                                    unwrap<Constant>(LHSConstant),
                                    unwrap<Constant>(RHSConstant)));
}

LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef B, LLVMValueRef *Values,
                                  unsigned NumValues) {
  std::vector<Value *> Vs;
  for (LLVMValueRef *I = Values, *E = Values + NumValues; I != E; ++I)
    Vs.push_back(unwrap(*I));

  return wrap(unwrap(B)->CreateRet(&Vs[0], NumValues));
}

LLVMValueRef LLVMBuildVICmp(LLVMBuilderRef B, LLVMIntPredicate Op,
                           LLVMValueRef LHS, LLVMValueRef RHS,
                           const char *Name) {
  return wrap(unwrap(B)->CreateVICmp(static_cast<ICmpInst::Predicate>(Op),
                                    unwrap(LHS), unwrap(RHS), Name));
}

LLVMValueRef LLVMBuildVFCmp(LLVMBuilderRef B, LLVMRealPredicate Op,
                           LLVMValueRef LHS, LLVMValueRef RHS,
                           const char *Name) {
  return wrap(unwrap(B)->CreateVFCmp(static_cast<FCmpInst::Predicate>(Op),
                                    unwrap(LHS), unwrap(RHS), Name));
}

LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef B, LLVMValueRef V,
                                unsigned Index, const char *Name) {
  return wrap(unwrap(B)->CreateGetResult(unwrap(V), Index, Name));
}

