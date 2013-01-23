#include <Python.h>
#include <llvm/ADT/SmallVector.h>

static
PyObject* small_vector_from_types(PyObject* self, PyObject* args) {
    using llvm::Type;
    using llvm::SmallVector_Type;
    SmallVector_Type* SV = new SmallVector_Type;
    Py_ssize_t size = PyTuple_Size(args);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject* cap = PyTuple_GetItem(args, i);
        Type* type = (Type*)PyCapsule_GetPointer(cap, "llvm::Type");
        SV->push_back(type);
    }
    return pycapsule_new(SV, "llvm::SmallVector_Type");
}

static PyMethodDef extra_methodtable[] = {
#define method(func) { #func, (PyCFunction)func, METH_VARARGS, NULL }
method( small_vector_from_types ),
{ NULL }
#undef method
};
