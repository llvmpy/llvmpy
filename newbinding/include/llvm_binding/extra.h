#include <Python.h>
#include <llvm/ADT/SmallVector.h>
#include <llvm/Value.h>
#include <llvm/Support/raw_ostream.h>


namespace extra{
    using namespace llvm;
    
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

}

static
PyObject* make_raw_ostream_for_printing(PyObject* self, PyObject* args) {
    using extra::raw_svector_ostream_helper;
    using llvm::raw_svector_ostream;
    
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    raw_svector_ostream* RSOH = raw_svector_ostream_helper::create();
    return pycapsule_new(RSOH, "llvm::raw_ostream",
                         "llvm::raw_svector_ostream");
}

static
PyObject* make_small_vector_from_types(PyObject* self, PyObject* args) {
    using llvm::Type;
    typedef llvm::SmallVector<llvm::Type*, 8> SmallVector_Type;
    
    SmallVector_Type* SV = new SmallVector_Type;
    Py_ssize_t size = PyTuple_Size(args);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject* cap = PyTuple_GetItem(args, i);
        if (!cap) {
            return NULL;
        }
        Type* type = (Type*)PyCapsule_GetPointer(cap, "llvm::Type");
        if (!type) {
            return NULL;
        }
        SV->push_back(type);
    }
    return pycapsule_new(SV, "llvm::SmallVector<llvm::Type*,8>");
}

static PyMethodDef extra_methodtable[] = {
    #define method(func) { #func, (PyCFunction)func, METH_VARARGS, NULL }
    method( make_raw_ostream_for_printing ),
    method( make_small_vector_from_types ),
    #undef method
    { NULL }
};


////////////

PyObject* Value_use_iterator_to_list(llvm::Value* val){
    typedef llvm::Value::use_iterator iterator;
    PyObject* list = PyList_New(0);
    for (iterator it = val->use_begin(), end = val->use_end(); it != end; ++it) {
        PyObject* cap = pycapsule_new(*it, "llvm::Value", "llvm::User");
        PyList_Append(list, cap);
    }
    return list;
}

