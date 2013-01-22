#ifndef LLVMPY_CAPSULE_CONTEXT_H_
#define LLVMPY_CAPSULE_CONTEXT_H_

#include <iostream>
#include <ctime>

typedef PyObject* Destructor_Fn;

struct CapsuleContext {
    const char*     className;
    
    CapsuleContext(const char* cn)
    : className(cn)
    { }
};


#endif //LLVMPY_CAPSULE_CONTEXT_H_

