/**
 * These are some "extra" functions not available in the standard LLVM-C
 * bindings, but are required / good-to-have inorder to implement the
 * Python bindings.
 */

#include <cassert>
#include <cstdlib>
#include <cstring>
#include <sstream>

#include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Constants.h"
#include "llvm/DerivedTypes.h"
#include "llvm/GlobalVariable.h"
#include "llvm/TypeSymbolTable.h"
#include "llvm/ModuleProvider.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/CallSite.h"
#include "llvm/IntrinsicInst.h"
#include "llvm/Analysis/Verifier.h"

#include "llvm-c/Core.h"

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

#if 0 /* after LLVM 2.3! */
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
#endif

LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef B, LLVMValueRef *Values,
                                  unsigned NumValues) {
  std::vector<Value *> Vs;
  for (LLVMValueRef *I = Values, *E = Values + NumValues; I != E; ++I)
    Vs.push_back(unwrap(*I));

  return wrap(unwrap(B)->CreateRet(&Vs[0], NumValues));
}

LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef B, LLVMValueRef V,
                                unsigned Index, const char *Name) {
  return wrap(unwrap(B)->CreateGetResult(unwrap(V), Index, Name));
}

LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef M, int ID,
    LLVMTypeRef *Types, unsigned Count)
{
    std::vector<const Type*> Tys;
    for (LLVMTypeRef *I = Types, *E = Types + Count; I != E; ++I)
        Tys.push_back(unwrap(*I));
  
    Function *intfunc = Intrinsic::getDeclaration(unwrap(M),
        Intrinsic::ID(ID), &Tys[0], Count);

    return wrap(intfunc);
}

LLVMModuleRef LLVMGetModuleFromBitcode(const char *BC, unsigned Len,
                                       char **OutMessage)
{
    MemoryBuffer *mb = MemoryBuffer::getMemBufferCopy(BC, BC+Len);
    if (!mb)
        return NULL;

    std::string msg;
    LLVMModuleRef mr = wrap(ParseBitcodeFile(mb, &msg));
    if (!mr)
        *OutMessage = strdup(msg.c_str());

    delete mb;
    return mr;
}

unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef M, unsigned *Len)
{
    std::ostringstream buf;
    WriteBitcodeToFile(unwrap(M), buf);
    const std::string& s = buf.str();
    size_t len = s.size();
    unsigned char *bytes = (unsigned char *)malloc(len);
    if (!bytes)
        return NULL;
    memcpy(bytes, s.data(), len);
    *Len = len;
    return bytes;
}
