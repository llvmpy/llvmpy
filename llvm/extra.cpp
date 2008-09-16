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
#include "llvm/Assembly/Parser.h"
// +includes for passes
#include "llvm/PassManager.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/Transforms/Scalar.h"
#include "llvm/Transforms/IPO.h"
#include "llvm/Transforms/Utils/UnifyFunctionExitNodes.h"
#include "llvm/Transforms/Instrumentation.h"
// -includes for passes

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

unsigned LLVMModuleGetPointerSize(LLVMModuleRef M)
{
    Module::PointerSize p = unwrap(M)->getPointerSize();
    if (p == Module::Pointer32)
        return 32;
    else if (p == Module::Pointer64)
        return 64;
    return 0;
}

LLVMValueRef LLVMModuleGetOrInsertFunction(LLVMModuleRef M, 
    const char *Name, LLVMTypeRef FunctionTy)
{
    FunctionType *ft = unwrap<FunctionType>(FunctionTy);
    Constant *f = unwrap(M)->getOrInsertFunction(Name, ft);
    return wrap(f);
}

#define inst_checkfn(ourfn, llvmfn)                         \
    unsigned ourfn (LLVMValueRef I) {                       \
        return unwrap<Instruction>(I)-> llvmfn () ? 1 : 0;  \
    }

inst_checkfn(LLVMInstIsTerminator,  isTerminator)
inst_checkfn(LLVMInstIsBinaryOp,    isBinaryOp)
inst_checkfn(LLVMInstIsShift,       isShift)
inst_checkfn(LLVMInstIsCast,        isCast)
inst_checkfn(LLVMInstIsLogicalShift,isLogicalShift)
inst_checkfn(LLVMInstIsArithmeticShift,isArithmeticShift)
inst_checkfn(LLVMInstIsAssociative, isAssociative)
inst_checkfn(LLVMInstIsCommutative, isCommutative)
inst_checkfn(LLVMInstIsTrapping,    isTrapping)

const char *LLVMInstGetOpcodeName(LLVMValueRef I)
{
    return unwrap<Instruction>(I)->getOpcodeName();
}

unsigned LLVMInstGetOpcode(LLVMValueRef I)
{
    return unwrap<Instruction>(I)->getOpcode();
}

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

LLVMModuleRef LLVMGetModuleFromAssembly(const char *A, unsigned Len,
                                        char **OutMessage)
{
    ParseError e;

    Module *MP = ParseAssemblyString(A, NULL /*unused within!*/, &e);
    if (!MP) {
        *OutMessage = strdup(e.getMessage().c_str());
        return NULL;
    }

    return wrap(MP);
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

/* passes */

#define define_pass(P)                              \
void LLVMAdd ## P ## Pass (LLVMPassManagerRef PM) { \
  unwrap(PM)->add( create ## P ## Pass ());         \
}

define_pass( AggressiveDCE )
define_pass( ArgumentPromotion )
define_pass( BlockPlacement )
define_pass( BreakCriticalEdges )
define_pass( CodeGenPrepare )
define_pass( CondPropagation )
define_pass( ConstantMerge )
//LLVM-C define_pass( ConstantPropagation )
define_pass( DeadCodeElimination )
define_pass( DeadArgElimination )
define_pass( DeadTypeElimination )
define_pass( DeadInstElimination )
define_pass( DeadStoreElimination )
define_pass( GCSE )
define_pass( GlobalDCE )
define_pass( GlobalOptimizer )
//LLVM-C define_pass( GVN )
define_pass( GVNPRE )
define_pass( IndMemRem )
define_pass( IndVarSimplify )
define_pass( FunctionInlining )
define_pass( BlockProfiler )
define_pass( EdgeProfiler )
define_pass( FunctionProfiler )
define_pass( NullProfilerRS )
define_pass( RSProfiling )
//LLVM-C define_pass( InstructionCombining )
/* we support only internalize(true) */
ModulePass *createInternalizePass() { return llvm::createInternalizePass(true); }
define_pass( Internalize )
define_pass( IPConstantPropagation )
define_pass( IPSCCP )
define_pass( JumpThreading )
define_pass( LCSSA )
define_pass( LICM )
define_pass( LoopDeletion )
define_pass( LoopExtractor )
define_pass( SingleLoopExtractor )
define_pass( LoopIndexSplit )
define_pass( LoopStrengthReduce )
define_pass( LoopRotate )
define_pass( LoopUnroll )
define_pass( LoopUnswitch )
define_pass( LoopSimplify )
define_pass( LowerAllocations )
define_pass( LowerInvoke )
define_pass( LowerSetJmp )
define_pass( LowerSwitch )
//LLVM-C define_pass( PromoteMemoryToRegister )
define_pass( MemCpyOpt )
define_pass( UnifyFunctionExitNodes )
define_pass( PredicateSimplifier )
define_pass( PruneEH )
define_pass( RaiseAllocations )
//LLVM-C define_pass( Reassociate )
define_pass( DemoteRegisterToMemory )
define_pass( ScalarReplAggregates )
define_pass( SCCP )
define_pass( SimplifyLibCalls )
//LLVM-C define_pass( CFGSimplification )
define_pass( StripSymbols )
define_pass( StripDeadPrototypes )
define_pass( StructRetPromotion )
define_pass( TailCallElimination )
define_pass( TailDuplication )

