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

/**
 * These are some "extra" functions not available in the standard LLVM-C
 * bindings, but are required / good-to-have inorder to implement the
 * Python bindings.
 */

// standard includes
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <sstream>

// LLVM includes
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
#include "llvm/System/DynamicLibrary.h"
#include "llvm/PassManager.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/Transforms/Scalar.h"
#include "llvm/Transforms/IPO.h"
#include "llvm/Transforms/Utils/UnifyFunctionExitNodes.h"
#include "llvm/Transforms/Instrumentation.h"

// LLVM-C includes
#include "llvm-c/Core.h"

// our includes
#include "extra.h"

//using namespace llvm;

/* Helper method for LLVMDumpXXXToString() methods. */
template <typename W, typename UW>
char *do_print(W obj)
{
    std::ostringstream buf;
    UW *p = llvm::unwrap(obj);
    assert(p);
    p->print(buf);
    return strdup(buf.str().c_str());
}

char *LLVMDumpModuleToString(LLVMModuleRef module)
{
    std::ostringstream buf;
    llvm::Module *p = llvm::unwrap(module);
    assert(p);
    p->print(buf, NULL);
    return strdup(buf.str().c_str());
}

char *LLVMDumpTypeToString(LLVMTypeRef type)
{
    return do_print<LLVMTypeRef, llvm::Type>(type);
}

char *LLVMDumpValueToString(LLVMValueRef value)
{
    return do_print<LLVMValueRef, llvm::Value>(value);
}

LLVMValueRef LLVMConstVICmp(LLVMIntPredicate predicate, LLVMValueRef lhs,
    LLVMValueRef rhs)
{
    llvm::Constant *lhsp = llvm::unwrap<llvm::Constant>(lhs);
    assert(lhsp);
    llvm::Constant *rhsp = llvm::unwrap<llvm::Constant>(rhs);
    assert(rhsp);

    llvm::Constant *vicmp =
        llvm::ConstantExpr::getVICmp(predicate, lhsp, rhsp);
    return llvm::wrap(vicmp);
}
    
LLVMValueRef LLVMConstVFCmp(LLVMRealPredicate predicate, LLVMValueRef lhs,
    LLVMValueRef rhs)
{
    llvm::Constant *lhsp = llvm::unwrap<llvm::Constant>(lhs);
    assert(lhsp);
    llvm::Constant *rhsp = llvm::unwrap<llvm::Constant>(rhs);
    assert(rhsp);

    llvm::Constant *vfcmp =
        llvm::ConstantExpr::getVFCmp(predicate, lhsp, rhsp);
    return llvm::wrap(vfcmp);
}

LLVMValueRef LLVMBuildVICmp(LLVMBuilderRef builder, LLVMIntPredicate predicate,
    LLVMValueRef lhs, LLVMValueRef rhs, const char *name)
{
    llvm::IRBuilder<> *builderp = llvm::unwrap(builder);
    assert(builderp);

    llvm::Value *lhsp = llvm::unwrap(lhs);
    assert(lhsp);
    llvm::Value *rhsp = llvm::unwrap(rhs);
    assert(rhsp);

    llvm::Value *inst = builderp->CreateVICmp(
        static_cast<llvm::CmpInst::Predicate>(predicate),
        lhsp, rhsp, name);
    return llvm::wrap(inst);
}

LLVMValueRef LLVMBuildVFCmp(LLVMBuilderRef builder, LLVMRealPredicate predicate,
    LLVMValueRef lhs, LLVMValueRef rhs, const char *name)
{
    llvm::IRBuilder<> *builderp = llvm::unwrap(builder);
    assert(builderp);

    llvm::Value *lhsp = llvm::unwrap(lhs);
    assert(lhsp);
    llvm::Value *rhsp = llvm::unwrap(rhs);
    assert(rhsp);

    llvm::Value *inst = builderp->CreateVFCmp(
        static_cast<llvm::CmpInst::Predicate>(predicate),
        lhsp, rhsp, name);
    return llvm::wrap(inst);
}

unsigned LLVMModuleGetPointerSize(LLVMModuleRef module)
{
    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    llvm::Module::PointerSize p = modulep->getPointerSize();
    if (p == llvm::Module::Pointer32)
        return 32;
    else if (p == llvm::Module::Pointer64)
        return 64;
    return 0;
}

LLVMValueRef LLVMModuleGetOrInsertFunction(LLVMModuleRef module,
    const char *name, LLVMTypeRef function_type)
{
    assert(name);

    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    llvm::FunctionType *ftp = llvm::unwrap<llvm::FunctionType>(function_type);
    assert(ftp);

    llvm::Constant *f = modulep->getOrInsertFunction(name, ftp);
    return wrap(f);
}

int LLVMHasInitializer(LLVMValueRef global_var)
{
    llvm::GlobalVariable *gvp = llvm::unwrap<llvm::GlobalVariable>(global_var);
    assert(gvp);

    return gvp->hasInitializer();
}

#define inst_checkfn(ourfn, llvmfn)                 \
unsigned ourfn (LLVMValueRef v) {                   \
    llvm::Instruction *ip = llvm::unwrap<llvm::Instruction>(v); \
    assert(ip);                                     \
    return ip-> llvmfn () ? 1 : 0;                  \
}

inst_checkfn(LLVMInstIsTerminator,      isTerminator)
inst_checkfn(LLVMInstIsBinaryOp,        isBinaryOp)
inst_checkfn(LLVMInstIsShift,           isShift)
inst_checkfn(LLVMInstIsCast,            isCast)
inst_checkfn(LLVMInstIsLogicalShift,    isLogicalShift)
inst_checkfn(LLVMInstIsArithmeticShift, isArithmeticShift)
inst_checkfn(LLVMInstIsAssociative,     isAssociative)
inst_checkfn(LLVMInstIsCommutative,     isCommutative)
inst_checkfn(LLVMInstIsTrapping,        isTrapping)

const char *LLVMInstGetOpcodeName(LLVMValueRef inst)
{
    llvm::Instruction *instp = llvm::unwrap<llvm::Instruction>(inst);
    assert(instp);
    return instp->getOpcodeName();
}

unsigned LLVMInstGetOpcode(LLVMValueRef inst)
{
    llvm::Instruction *instp = llvm::unwrap<llvm::Instruction>(inst);
    assert(instp);
    return instp->getOpcode();
}

/* llvm::unwrap a set of `n' wrapped objects starting at `values',
 * into a vector of pointers to llvm::unwrapped objects `out'. */
template <typename W, typename UW>
void unwrap_vec(W *values, unsigned n, std::vector<UW *>& out)
{
    out.clear();

    while (n--) {
        UW *p = llvm::unwrap(*values);
        assert(p);
        out.push_back(p);
        ++values;
    }
}

/* Same as llvm::unwrap_vec, but use a vector of const pointers. */
template <typename W, typename UW>
void unwrap_cvec(W *values, unsigned n, std::vector<const UW *>& out)
{
    out.clear();

    while (n--) {
        UW *p = llvm::unwrap(*values);
        assert(p);
        out.push_back(p);
        ++values;
    }
}

LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef builder, 
    LLVMValueRef *values, unsigned n_values)
{
    assert(values);

    std::vector<llvm::Value *> values_vec;
    unwrap_vec(values, n_values, values_vec);

    llvm::IRBuilder<> *builderp = llvm::unwrap(builder);
    assert(builderp);

    return llvm::wrap(builderp->CreateAggregateRet(&values_vec[0], values_vec.size()));
}

LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef builder, 
    LLVMValueRef value, unsigned index, const char *name)
{
    assert(name);

    llvm::IRBuilder<> *builderp = llvm::unwrap(builder);
    assert(builderp);

    return llvm::wrap(builderp->CreateExtractValue(llvm::unwrap(value), index, name));
}

LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef module, int id,
    LLVMTypeRef *types, unsigned n_types)
{
    assert(types);

    std::vector<const llvm::Type*> types_vec;
    unwrap_cvec(types, n_types, types_vec);

    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    llvm::Function *intfunc = llvm::Intrinsic::getDeclaration(modulep, 
        llvm::Intrinsic::ID(id), &types_vec[0], types_vec.size());

    return wrap(intfunc);
}

LLVMModuleRef LLVMGetModuleFromAssembly(const char *asmtext, unsigned txtlen,
    char **out)
{
    assert(asmtext);
    assert(out);

    llvm::Module *modulep;
    llvm::ParseError error;
    if (!(modulep = llvm::ParseAssemblyString(asmtext, NULL /*unused within!*/, 
                        &error))) {
        *out = strdup(error.getMessage().c_str());
        return NULL;
    }

    return wrap(modulep);
}

LLVMModuleRef LLVMGetModuleFromBitcode(const char *bitcode, unsigned bclen,
    char **out)
{
    assert(bitcode);
    assert(out);

    llvm::MemoryBuffer *mbp;
    if (!(mbp = llvm::MemoryBuffer::getMemBufferCopy(bitcode, bitcode+bclen)))
        return NULL;

    std::string msg;
    llvm::Module *modulep;
    if (!(modulep = llvm::ParseBitcodeFile(mbp, &msg)))
        *out = strdup(msg.c_str());

    delete mbp;
    return wrap(modulep);
}

unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef module, unsigned *lenp)
{
    assert(lenp);

    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    /* get bc into a string */
    std::ostringstream buf;
    llvm::WriteBitcodeToFile(modulep, buf);
    const std::string& bc = buf.str();

    /* and then into a malloc()-ed block */
    size_t bclen = bc.size();
    unsigned char *bytes = (unsigned char *)malloc(bclen);
    if (!bytes)
        return NULL;
    memcpy(bytes, bc.data(), bclen);

    /* return */
    *lenp = bclen;
    return bytes;
}

/* Return 0 on failure (with errmsg filled in), 1 on success. */
unsigned LLVMLoadLibraryPermanently(const char* filename, char **errmsg)
{
    assert(filename);
    assert(errmsg);

    /* Note: the LLVM API returns true on failure. Don't ask why. */
    std::string msg;
    if (llvm::sys::DynamicLibrary::LoadLibraryPermanently(filename, &msg)) {
        *errmsg = strdup(msg.c_str());
        return 0;
    }

    return 1;
}


/* Passes. A few passes (listed below) are used directly from LLVM-C,
 * rest are defined here.
 *
 *  ConstantPropagation
 *  GVN
 *  InstructionCombining
 *  PromoteMemoryToRegister
 *  Reassociate
 *  CFGSimplification
 */

#define define_pass(P)                                   \
void LLVMAdd ## P ## Pass (LLVMPassManagerRef passmgr) { \
    using namespace llvm;                                \
    llvm::PassManagerBase *pmp = llvm::unwrap(passmgr);  \
    assert(pmp);                                         \
    pmp->add( create ## P ## Pass ());                   \
}

define_pass( AggressiveDCE )
define_pass( ArgumentPromotion )
define_pass( BlockPlacement )
define_pass( BreakCriticalEdges )
define_pass( CodeGenPrepare )
define_pass( CondPropagation )
define_pass( ConstantMerge )
define_pass( DeadCodeElimination )
define_pass( DeadArgElimination )
define_pass( DeadTypeElimination )
define_pass( DeadInstElimination )
define_pass( DeadStoreElimination )
/* define_pass( GCSE ): removed in LLVM 2.4 */
define_pass( GlobalDCE )
define_pass( GlobalOptimizer )
define_pass( GVNPRE )
define_pass( IndMemRem )
define_pass( IndVarSimplify )
define_pass( FunctionInlining )
define_pass( BlockProfiler )
define_pass( EdgeProfiler )
define_pass( FunctionProfiler )
define_pass( NullProfilerRS )
define_pass( RSProfiling )
/* we support only internalize(true) */
llvm::ModulePass *createInternalizePass() { return llvm::createInternalizePass(true); }
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
define_pass( MemCpyOpt )
define_pass( UnifyFunctionExitNodes )
define_pass( PredicateSimplifier )
define_pass( PruneEH )
define_pass( RaiseAllocations )
define_pass( DemoteRegisterToMemory )
define_pass( ScalarReplAggregates )
define_pass( SCCP )
define_pass( SimplifyLibCalls )
define_pass( StripSymbols )
define_pass( StripDeadPrototypes )
define_pass( StructRetPromotion )
define_pass( TailCallElimination )
define_pass( TailDuplication )

