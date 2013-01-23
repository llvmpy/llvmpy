#include <Python.h>
#include <llvm/ADT/SmallVector.h>
#include <llvm/Support/raw_ostream.h>

namespace llvm{

class Type; //forward declaration

class raw_svector_ostream_helper: public raw_svector_ostream {
    SmallVectorImpl<char> *SV;
public:
    static
    raw_svector_ostream_helper* create(){
        SmallVectorImpl<char>* sv = new SmallVector<char, 16>();
        return new raw_svector_ostream_helper(sv);
    }

    ~raw_svector_ostream_helper(){
        delete SV;
    }

protected:

    explicit
    raw_svector_ostream_helper(SmallVectorImpl<char>* sv)
    : raw_svector_ostream(*sv), SV(sv) {}

private:
    // no copy
    raw_svector_ostream_helper(const raw_svector_ostream_helper&);
    // no assign
    void operator = (const raw_svector_ostream_helper&);
};


class SmallVector_Type : public SmallVector<Type*, 8> {
public:
    static
    SmallVector_Type* fromPySequence(PyObject* obj) {
        SmallVector_Type* SV = new SmallVector_Type;
        Py_ssize_t sz = PySequence_Size(obj);
        for (Py_ssize_t i = 0; i < sz; ++i) {
            PyObject* item = PySequence_GetItem(obj, i);
            PyObject* cap = PyObject_GetAttrString(item, "_ptr");
            Type* type = (Type*)PyCapsule_GetPointer(cap, "llvm::Type");
            SV->push_back(type);
            Py_XDECREF(cap);
            Py_XDECREF(item);
        }
        return SV;
    }
};

    
} // end namespace llvm

