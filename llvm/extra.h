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

#ifndef LLVM_PY_EXTRA_H
#define LLVM_PY_EXTRA_H

#ifdef __cplusplus
extern "C" {
#endif

/* Notes:
 *  - Some returned strings must be disposed of by LLVMDisposeMessage. These are
 *    indicated in the comments. Where it is not indicated, DO NOT call dispose.
 */

/* Wraps llvm::Module::print(). Dispose the returned string after use, via
 * LLVMDisposeMessage(). */
char *LLVMDumpModuleToString(LLVMModuleRef module);

/* Wraps llvm::Type::print(). Dispose the returned string after use, via
 * LLVMDisposeMessage(). */
char *LLVMDumpTypeToString(LLVMTypeRef type);

/* Wraps llvm::Value::print(). Dispose the returned string after use, via
 * LLVMDisposeMessage(). */
char *LLVMDumpValueToString(LLVMValueRef Val);

/* Wraps llvm::IRBuilder::CreateRet(). */
LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef bulder, LLVMValueRef *values,
    unsigned n_values);

/* Wraps llvm::IRBuilder::CreateGetResult(). */
LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef builder, LLVMValueRef value,
    unsigned index, const char *name);

/* Wraps llvm::ConstantExpr::getVICmp(). */
LLVMValueRef LLVMConstVICmp(LLVMIntPredicate predicate, LLVMValueRef lhs,
    LLVMValueRef rhs);

/* Wraps llvm::ConstantExpr::getVFCmp(). */
LLVMValueRef LLVMConstVFCmp(LLVMRealPredicate predicate, LLVMValueRef lhs,
    LLVMValueRef rhs);

/* Wraps llvm::IRBuilder::CreateVICmp(). */    
LLVMValueRef LLVMBuildVICmp(LLVMBuilderRef builder, LLVMIntPredicate predicate,
    LLVMValueRef lhs, LLVMValueRef rhs, const char *name);

/* Wraps llvm::IRBuilder::CreateVFCmp(). */    
LLVMValueRef LLVMBuildVFCmp(LLVMBuilderRef builder, LLVMRealPredicate predicate,
    LLVMValueRef lhs, LLVMValueRef rhs, const char *name);
    
/* Wraps llvm::Intrinsic::getDeclaration(). */
LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef builder, int id,
    LLVMTypeRef *types, unsigned n_types);

/* Wraps llvm::Module::getPointerSize(). */
unsigned LLVMModuleGetPointerSize(LLVMModuleRef module);

/* Wraps llvm::Module::getOrInsertFunction(). */
LLVMValueRef LLVMModuleGetOrInsertFunction(LLVMModuleRef module, 
    const char *name, LLVMTypeRef function_type);

/* Wraps llvm::GlobalVariable::hasInitializer(). */    
int LLVMHasInitializer(LLVMValueRef global_var);
    
/* The following functions wrap various llvm::Instruction::isXXX() functions.
 * All of them take an instruction and return 0 (isXXX returned false) or 1
 * (isXXX returned false). */
unsigned LLVMInstIsTerminator      (LLVMValueRef inst);
unsigned LLVMInstIsBinaryOp        (LLVMValueRef inst);
unsigned LLVMInstIsShift           (LLVMValueRef inst);
unsigned LLVMInstIsCast            (LLVMValueRef inst);
unsigned LLVMInstIsLogicalShift    (LLVMValueRef inst);
unsigned LLVMInstIsArithmeticShift (LLVMValueRef inst);
unsigned LLVMInstIsAssociative     (LLVMValueRef inst);
unsigned LLVMInstIsCommutative     (LLVMValueRef inst);
unsigned LLVMInstIsTrapping        (LLVMValueRef inst);

/* Wraps llvm::Instruction::getOpcodeName(). */
const char *LLVMInstGetOpcodeName(LLVMValueRef inst);

/* Wraps llvm::Instruction::getOpcode(). */
unsigned LLVMInstGetOpcode(LLVMValueRef inst);

/* Wraps llvm::ParseAssemblyString(). Returns a module reference or NULL (with
 * `out' pointing to an error message). Dispose error message after use, via
 * LLVMDisposeMessage(). */
LLVMModuleRef LLVMGetModuleFromAssembly(const char *asmtxt, unsigned txten,
    char **out);

/* Wraps llvm::ParseBitcodeFile(). Returns a module reference or NULL (with
 * `out' pointing to an error message). Dispose error message after use, via
 * LLVMDisposeMessage(). */
LLVMModuleRef LLVMGetModuleFromBitcode(const char *bc, unsigned bclen,
    char **out);

/* Returns pointer to a heap-allocated block of `*len' bytes containing bit code
 * for the given module. NULL on error. */
unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef module, unsigned *len);

/* Wraps llvm::sys::DynamicLibrary::LoadLibraryPermanently(). Returns 0 on
 * failure (with errmsg filled in) and 1 on success. Dispose error message after
 * use, via LLVMDisposeMessage(). */
unsigned LLVMLoadLibraryPermanently(const char* filename, char **errmsg);

/* Passes. A few passes (listed below) are used directly from LLVM-C,
 * rest are declared here.
 *
 *  ConstantPropagation
 *  GVN
 *  InstructionCombining
 *  PromoteMemoryToRegister
 *  Reassociate
 *  CFGSimplification
 */

#define declare_pass(P) \
    void LLVMAdd ## P ## Pass (LLVMPassManagerRef PM);

declare_pass( AggressiveDCE )
declare_pass( ArgumentPromotion )
declare_pass( BlockPlacement )
declare_pass( BreakCriticalEdges )
declare_pass( CodeGenPrepare )
declare_pass( CondPropagation )
declare_pass( ConstantMerge )
declare_pass( DeadCodeElimination )
declare_pass( DeadArgElimination )
declare_pass( DeadTypeElimination )
declare_pass( DeadInstElimination )
declare_pass( DeadStoreElimination )
/* declare_pass( GCSE ): removed in LLVM 2.4. */
declare_pass( GlobalDCE )
declare_pass( GlobalOptimizer )
declare_pass( GVNPRE )
declare_pass( IndMemRem )
declare_pass( IndVarSimplify )
declare_pass( FunctionInlining )
declare_pass( BlockProfiler )
declare_pass( EdgeProfiler )
declare_pass( FunctionProfiler )
declare_pass( NullProfilerRS )
declare_pass( RSProfiling )
declare_pass( Internalize )
declare_pass( IPConstantPropagation )
declare_pass( IPSCCP )
declare_pass( JumpThreading )
declare_pass( LCSSA )
declare_pass( LICM )
declare_pass( LoopDeletion )
declare_pass( LoopExtractor )
declare_pass( SingleLoopExtractor )
declare_pass( LoopIndexSplit )
declare_pass( LoopStrengthReduce )
declare_pass( LoopRotate )
declare_pass( LoopUnroll )
declare_pass( LoopUnswitch )
declare_pass( LoopSimplify )
declare_pass( LowerAllocations )
declare_pass( LowerInvoke )
declare_pass( LowerSetJmp )
declare_pass( LowerSwitch )
declare_pass( MemCpyOpt )
declare_pass( UnifyFunctionExitNodes )
declare_pass( PredicateSimplifier )
declare_pass( PruneEH )
declare_pass( RaiseAllocations )
declare_pass( DemoteRegisterToMemory )
declare_pass( ScalarReplAggregates )
declare_pass( SCCP )
declare_pass( SimplifyLibCalls )
declare_pass( StripSymbols )
declare_pass( StripDeadPrototypes )
declare_pass( StructRetPromotion )
declare_pass( TailCallElimination )
declare_pass( TailDuplication )

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* LLVM_PY_EXTRA_H */

