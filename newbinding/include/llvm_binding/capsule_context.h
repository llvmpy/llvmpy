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
    if (!ptr) {
        Py_RETURN_NONE;
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


static
PyObject* pycapsule_new(const void* ptr,
                        const char* basename,
                        const char* classname=NULL)
{
    // Use const_cast to strip the constantness.
    // Let the user take the responsibility.
    return pycapsule_new(const_cast<void*>(ptr), basename, classname);
}


#endif //LLVMPY_CAPSULE_CONTEXT_H_

