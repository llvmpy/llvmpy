#ifndef LLVMPY_CAPSULE_CONTEXT_H_
#define LLVMPY_CAPSULE_CONTEXT_H_
#include <iostream>
#include <ctime>

typedef PyObject* Destructor_Fn;

static bool CapsuleContextDebug = false;

struct CapsuleContext {
    const char*     className;
    Destructor_Fn 	destructor;

    CapsuleContext(const char* cn, Destructor_Fn dtor=NULL)
    : className(cn), destructor(dtor) { }
};

void capsule_destructor(PyObject* capsule){
    using std::cerr;
    using std::endl;
    CapsuleContext* context = (CapsuleContext*)PyCapsule_GetContext(capsule);
    if (context->destructor) {
        if (CapsuleContextDebug) {
            cerr << clock()
                 << " == DEBUG =="
                 << " destroy pointer: "
                 << context->className
                 << endl;
        }
        PyObject_CallMethodObjArgs(context->destructor, capsule, NULL);
    } else {
        if (CapsuleContextDebug) {
            cerr << clock()
                 << " == DEBUG =="
                 << " keep pointer alive: "
                 << context->className
                 << endl;
        }
    }
    delete context;
}

void enable_capsule_dtor_debug(bool enabled){
    CapsuleContextDebug = enabled;
}

#endif //LLVMPY_CAPSULE_CONTEXT_H_

