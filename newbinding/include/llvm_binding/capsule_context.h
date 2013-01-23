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


static
PyObject* pycapsule_new(void* ptr,
                        const char* basename,
                        const char* classname=NULL)
{
    if (!classname) {
        classname = basename;
    }
    PyObject* cap = PyCapsule_New(ptr, basename, NULL);
    if (!cap) {
        PyErr_SetString(PyExc_TypeError, "Error creating new PyCapsule");
        return NULL;
    }
    CapsuleContext* context = new CapsuleContext(classname);
    if (PyCapsule_SetContext(cap, context)) {
        return NULL;
    }
    return cap;
}



#endif //LLVMPY_CAPSULE_CONTEXT_H_

