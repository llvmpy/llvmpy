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

