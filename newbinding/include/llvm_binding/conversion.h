#include <Python.h>
#include <llvm/Support/Casting.h>
#include <llvm/ADT/StringRef.h>

// python object unwrapper

static
int py_str_to(PyObject *strobj, llvm::StringRef &strref){
    // type check
    if (!PyString_Check(strobj)) {
         // raises TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting a str");
        return 0;
    }
    // get len and buffer
    const Py_ssize_t len = PyString_Size(strobj);
    const char * buf = PyString_AsString(strobj);
    if (!buf) {
        // raises TypeError
        return 0;
    }
    // set output
    strref = llvm::StringRef(buf, len);
    // success
    return 1;
}

static
int py_int_to(PyObject *intobj, unsigned & val){
    if (!PyInt_Check(intobj)) {
        // raise TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting an int");
        return 0;
    }
    val = PyInt_AsUnsignedLongMask(intobj);
    // success
    return 1;
}

static
int py_bool_to(PyObject *boolobj, bool & val){
    if (!PyBool_Check(boolobj)) {
        // raise TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting a bool");
        return 0;
    }
    if (boolobj == Py_True) {
        val = true;
    } else if (boolobj == Py_False) {
        val = false;
    } else {
        PyErr_SetString(PyExc_TypeError, "Invalid boolean object");
        return 0;
    }
    // success
    return 1;
}

// python object wrapper

static
PyObject* py_str_from(const std::string &str){
    return PyString_FromStringAndSize(str.c_str(), str.size());
}
//
//static
//PyObject* py_str_from(const llvm::StringRef *str){
//    return py_str_from(str->str());
//}

static
PyObject* py_bool_from(bool val){
    if (val) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static
PyObject* py_int_from(int val){
    return PyInt_FromLong(val);
}

// casting
template<class Td>
struct typecast {
    template<class Ts> static
    Td* from(Ts* src) {
        return llvm::dyn_cast<Td>(src);
    }

    static
    Td* from(void* src) {
        return static_cast<Td*>(src);
    }
};

