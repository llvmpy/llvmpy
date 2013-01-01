#ifndef LLVM_C_EXTRA_H_
#define LLVM_C_EXTRA_H_

#include <llvm-c/Core.h>


#ifdef __cplusplus
    extern "C" {
#endif

// Resurrect from llvm-c/Core.h
#define DEFINE_SIMPLE_CONVERSION_FUNCTIONS(ty, ref)     \
inline ty *unwrap(ref P) {                              \
    return reinterpret_cast<ty*>(P);                    \
}                                                       \
                                                        \
inline ref wrap(const ty *P) {                          \
    return reinterpret_cast<ref>(const_cast<ty*>(P));   \
}

typedef struct LLVMOpaqueEngineBuilder *LLVMEngineBuilderRef;
typedef struct LLVMOpaqueTargetMachine *LLVMTargetMachineRef;
typedef struct LLVMOpaqueNamedMD *LLVMNamedMDRef;
typedef struct LLVMOpaquePass *LLVMPassRef;

#ifdef __cplusplus
    }
#endif

#endif  //LLVM_C_EXTRA_H_

