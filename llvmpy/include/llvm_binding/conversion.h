#include <Python.h>
#include <llvm/Support/Casting.h>
#include <llvm/ADT/StringRef.h>

// python object unwrapper

static
int py_bytes_to(PyObject *bytesobj, llvm::StringRef &strref){
    // type check
    if (!PyBytes_Check(bytesobj)) {
        // raises TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting a bytes");
        return 0;
    }
    // get len and buffer
    const Py_ssize_t len = PyBytes_Size(bytesobj);
    const char * buf = PyBytes_AsString(bytesobj);
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
int py_str_to(PyObject *strobj, std::string &strref){
    // type check
    if (!PyString_Check(strobj)) {
        // raises TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting a str");
        return 0;
    }
    // get len and buffer
    const char * buf = PyString_AsString(strobj);
    if (!buf) {
        // raises TypeError
        return 0;
    }
    // set output
    strref = std::string(buf);
    // success
    return 1;
}


static
int py_str_to(PyObject *strobj, const char* &strref){
    // type check
    if (!PyString_Check(strobj)) {
        // raises TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting a str");
        return 0;
    }
    // get buffer
    strref = PyString_AsString(strobj);
    if (!strref) {
        // raises TypeError
        return 0;
    }
    // success
    return 1;
}


static
int py_int_to(PyObject *intobj, int64_t & val){
    if (!PyInt_Check(intobj) && !PyLong_Check(intobj)) {
        // raise TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting an int");
        return 0;
    }
    if (PyLong_Check(intobj)) {
        val = PyLong_AsLongLong(intobj);
    } else {
        val = PyInt_AsLong(intobj);
    }
    if (PyErr_Occurred()){
        return NULL;
    }
    // success
    return 1;
}



static
int py_int_to(PyObject *intobj, unsigned & val){
    if (!PyInt_Check(intobj) && !PyLong_Check(intobj)) {
        // raise TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting an int");
        return 0;
    }
    val = PyInt_AsUnsignedLongMask(intobj);
    // success
    return 1;
}

static
int py_int_to(PyObject *intobj, unsigned long long & val){
    if (!PyInt_Check(intobj) && !PyLong_Check(intobj)) {
        // raise TypeError;
        PyErr_SetString(PyExc_TypeError, "Expecting an int");
        return 0;
    }
    val = PyInt_AsUnsignedLongLongMask(intobj);
    // success
    return 1;

}

static
int py_int_to(PyObject *intobj, unsigned long & val){
    unsigned long long ull;
    if (py_int_to(intobj, ull)) {
        val = (unsigned long)ull;
        return 1;
    } else {
        return 0;
    }
}


static
int py_int_to(PyObject *intobj, void* & val){
    if (!PyInt_Check(intobj) && !PyLong_Check(intobj)) {
        // raise TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting an int");
        return 0;
    }
    val = PyLong_AsVoidPtr(intobj);
    // success
    return 1;
}

static
int py_float_to(PyObject *floatobj, double & val){
    if (!PyFloat_Check(floatobj)) {
        // raise TypeError
        PyErr_SetString(PyExc_TypeError, "Expecting a float");
        return 0;
    }
    val = PyFloat_AsDouble(floatobj);
    if (PyErr_Occurred()){
        return 0;
    }
    // success
    return 1;
}


static
int py_float_to(PyObject *floatobj, float & val){
    double db;
    int status = py_float_to(floatobj, db);
    if (status)
        val = db;
    return status;
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
    return PyString_FromStringAndSize(str.data(), str.size());
}


static
PyObject* py_bytes_from(const std::string &str){
    return PyBytes_FromStringAndSize(str.data(), str.size());
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
PyObject* py_int_from_signed(const long long & val){
    return PyLong_FromLongLong(val);
}

static
PyObject* py_int_from_unsigned(const unsigned long long & val){
    return PyLong_FromUnsignedLongLong(val);
}

static
PyObject* py_int_from_unsigned(void * addr){
    return PyLong_FromVoidPtr(addr);
}

static
PyObject* py_float_from(const double& val) {
    return PyFloat_FromDouble(val);
}

// casting
template<class Td>
struct typecast {
    template<class Ts> static
    Td* from(Ts* src) {
        // check why this is only used in Python3
        return llvm::dyn_cast<Td>(src);
    }

    static
    Td* from(void* src) {
        return static_cast<Td*>(src);
    }
};

template<class Td, class Tbase>
struct unwrap_as {
    static
    Td* from(void* src) {
        Tbase* base = static_cast<Tbase*>(src);
        return static_cast<Td*>(base);
    }
};

template<class Td>
struct cast_to_base {
    template<class Ts> static
    Td* from(Ts* src){
        return static_cast<Td*>(src);
    }
    
    template<class Ts> static
    const Td* from(const Ts* src){
        return static_cast<const Td*>(src);
    }
};
