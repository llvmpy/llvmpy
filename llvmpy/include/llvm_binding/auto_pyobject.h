#ifndef AUTO_PYOBJECT_H_
#define AUTO_PYOBJECT_H_

#include <Python.h>

class auto_pyobject{
    mutable PyObject* PO;
public:
    auto_pyobject(): PO(NULL) { }

    auto_pyobject(PyObject* po) : PO(po) { }

    auto_pyobject(const auto_pyobject& other) : PO(*other){
        other.PO = NULL;
    }

    ~auto_pyobject() {
        Py_XDECREF(PO);
    }

    bool operator ! () const {
        return !PO;
    }

    PyObject* operator * () const {
        return PO;
    }

    PyObject* get() const {
        return PO;
    }
private:
    // disable assign
    void operator = (const auto_pyobject&);
};

#endif AUTO_PYOBJECT_H_

