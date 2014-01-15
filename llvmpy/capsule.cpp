#include <Python.h>
#include <structmember.h>
#include <python3adapt.h>
#include <capsulethunk.h>
#include <llvm_binding/capsule_context.h>
#include <llvm_binding/auto_pyobject.h>
#include <string>
#include <sstream>

static PyObject* TheAPIModule = NULL;
static PyObject* TheCapsuleModule = NULL;
static PyObject* TheCapsuleClass = NULL;
static PyObject* TheWrapperClass = NULL;
static PyObject* TheCache = NULL;
static PyObject* TheAddrDtorDict = NULL;
static PyObject* TheClassesDict = NULL;
static PyObject* TheAddrRefCt = NULL;
static PyObject* ConstantOne = NULL;
static PyObject* TheDowncastModule = NULL;

static
PyObject* GetAPIModule(){
    if (NULL == TheAPIModule)
        TheAPIModule = PyImport_ImportModule("llvmpy._api");
    return TheAPIModule;
}

static
PyObject* GetCapsuleModule(){
    if (NULL == TheCapsuleModule)
        TheCapsuleModule = PyImport_ImportModule("llvmpy.capsule");
    return TheCapsuleModule;
}

static
PyObject* GetCapsuleClass() {
    if (NULL == TheCapsuleClass)
        TheCapsuleClass = PyObject_GetAttrString(GetCapsuleModule(),
                                                 "Capsule");
    return TheCapsuleClass;
}

static
PyObject* GetWrapperClass() {
    if (NULL == TheWrapperClass)
            TheWrapperClass = PyObject_GetAttrString(GetCapsuleModule(),
                                                     "Wrapper");
    return TheWrapperClass;
}

static
PyObject* GetCache() {
    if (NULL == TheCache)
            TheCache = PyObject_GetAttrString(GetCapsuleModule(), "_cache");
    return TheCache;
}

static
PyObject* GetAddrDtorDict() {
    if (NULL == TheAddrDtorDict)
            TheAddrDtorDict = PyObject_GetAttrString(GetCapsuleModule(),
                                                     "_addr2dtor");
    return TheAddrDtorDict;
}

static
PyObject* GetClassesDict() {
    if (NULL == TheClassesDict)
        TheClassesDict = PyObject_GetAttrString(GetCapsuleModule(),
                                                "_pyclasses");
    return TheClassesDict;
}

static
PyObject* GetAddrRefCt() {
    if (NULL == TheAddrRefCt)
        TheAddrRefCt = PyObject_GetAttrString(GetCapsuleModule(),
                                              "_addr2refct");
    return TheAddrRefCt;
}

static
PyObject* GetDowncastModule() {
    if (NULL == TheDowncastModule)
        TheDowncastModule = PyObject_GetAttrString(GetAPIModule(),
                                                   "downcast");
    return TheDowncastModule;

}

static
CapsuleContext* GetContext(PyObject *obj) {
    void* context = PyCapsule_GetContext(obj);
    if (!context) {
        PyErr_SetString(PyExc_TypeError, "PyCapsule has no context.");
        return NULL;
    }
    return static_cast<CapsuleContext*>(context);
}

static
PyObject* GetClassName(PyObject* obj) {
    CapsuleContext* context = GetContext(obj);
    if (!context) {
        return NULL;
    } else {
        return PyString_FromString(context->className);
    }
}

static
PyObject* getClassName(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }
    return GetClassName(obj);
}

static
PyObject* GetName(PyObject* obj) {
    const char* name = PyCapsule_GetName(obj);
    if (!name) return NULL;
    return PyString_FromString(name);
}

static
PyObject* getName(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)){
        return NULL;
    }
    return GetName(obj);
}

static
PyObject* GetPointer(PyObject* obj){
    void *pointer = PyCapsule_GetPointer(obj, PyCapsule_GetName(obj));
    if (!pointer) return NULL;
    return PyLong_FromVoidPtr(pointer);
}

static
PyObject* getPointer(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)){
        return NULL;
    }
    return GetPointer(obj);
}

static
bool Check(PyObject* obj){
    return PyCapsule_CheckExact(obj);
}

static
PyObject* check(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)){
        return NULL;
    }
    if (Check(obj)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}


static PyObject* Unwrap(PyObject* obj) {
    if (PyObject_IsInstance(obj, GetWrapperClass())) {
        return PyObject_GetAttrString(obj, "_ptr");
    } else {
        Py_INCREF(obj);
        return obj;
    }
}

/*
Unwrap a Wrapper instance into the underlying PyCapsule.
If `obj` is not a Wrapper instance, returns `obj`.
*/
static PyObject* unwrap(PyObject* self, PyObject* args) {
    PyObject *obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }
    return Unwrap(obj);
}

static bool HasOwnership(PyObject* obj) {
    PyObject* addr = GetPointer(obj);
    PyObject* name = GetName(obj);
    auto_pyobject nameaddr = PyTuple_Pack(2, name, addr);
    PyObject* dtor = PyDict_GetItem(GetAddrDtorDict(), *nameaddr);
    if (!dtor || dtor == Py_None) {
        return false;
    } else {
        return true;
    }
}

static PyObject* has_ownership(PyObject* self, PyObject* args) {
    PyObject *obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }
    if (HasOwnership(obj)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static
void NormalizeString(std::ostream &os, const char* str) {
    for(; *str; ++str){
        if (*str == ':') {
            os << '_';
            if(*(str + 1) == ':') { ++str; }
        } else {
            os << *str;
        }
    }
}

static
PyObject* WrapCore(PyObject *oldCap, bool owned) {
    auto_pyobject cap = PyObject_CallFunctionObjArgs(GetCapsuleClass(), oldCap,
                                                     NULL);
    auto_pyobject cls = PyObject_CallMethod(*cap, "get_class", "");
    auto_pyobject addr = GetPointer(oldCap);
    auto_pyobject name = GetName(oldCap);

    // look up cached object
    auto_pyobject cache_cls = PyObject_GetItem(GetCache(), *cls);
    Assert(*cache_cls);
    int addr_in_cache = PyMapping_HasKey(*cache_cls, *addr);

    PyObject* obj = NULL;
    if (addr_in_cache) {
        obj = PyObject_GetItem(*cache_cls, *addr);
    } else {
        if (!owned) {
            auto_pyobject hasDtor = PyObject_CallMethod(*cls, "_has_dtor", "");
            if (PyObject_IsTrue(*hasDtor)) {
                auto_pyobject key = PyTuple_Pack(2, *name, *addr);
                auto_pyobject val = PyObject_GetAttrString(*cls, "_delete_");

                int ok = PyDict_SetItem(GetAddrDtorDict(), *key, *val);
                Assert(ok != -1);
            }
        }
        obj = PyObject_CallMethod(*cap, "instantiate", "");
        int ok = PyObject_SetItem(*cache_cls, *addr, obj);
        Assert(ok != -1);
    }

    Assert(obj);
    return obj;
}

static
PyObject* Wrap(PyObject* cap, bool owned){
    if (!Check(cap)) {
        if (PyList_Check(cap)) {
            const int N = PyList_Size(cap);
            PyObject* result = PyList_New(N);

            for (int i = 0; i < N; ++i){
                PyObject* item = PyList_GetItem(cap, i);
                if (!item)
                    return NULL;
                PyObject* out = Wrap(item, false);
                if (!out) return NULL;
                if (-1 == PyList_SetItem(result, i, out))
                    return NULL;
            }

            return result;
        } else {
            Py_INCREF(cap);
            return cap;
        }
    }

    return WrapCore(cap, owned);
}


static
PyObject* wrap(PyObject* self, PyObject* args) {
    PyObject* obj;
    PyObject* owned = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &obj, &owned)) {
        return NULL;
    }
    bool ownedFlag = false;
    if (owned) {
        ownedFlag = PyObject_IsTrue(owned);
    }
    return Wrap(obj, ownedFlag);
}

static
PyObject* downcast(PyObject* self, PyObject* args) {
    PyObject *obj, *cls;
    if (!PyArg_ParseTuple(args, "OO", &obj, &cls)) {
        return NULL;
    }

    auto_pyobject objType = PyObject_Type(obj);

    if (*objType == cls) {
        Py_INCREF(obj);
        return obj;
    }

    PyObject* apiModule = GetAPIModule();

    auto_pyobject fromTy = PyObject_GetAttrString(obj, "_llvm_type_");
    auto_pyobject toTy = PyObject_GetAttrString(cls, "_llvm_type_");

    std::ostringstream oss;

    auto_pyobject fromTyStr = PyObject_Str(*fromTy);
    auto_pyobject toTyStr = PyObject_Str(*toTy);

    const char * fromCS = PyString_AsString(*fromTyStr);
    const char * toCS = PyString_AsString(*toTyStr);

    oss << "downcast_";
    NormalizeString(oss, fromCS);
    oss << "_to_";
    NormalizeString(oss, toCS);
    std::string fname = oss.str();

    auto_pyobject caster = PyObject_GetAttrString(GetDowncastModule(),
                                                  fname.c_str());

    if (!caster) {
        std::ostringstream oss;
        oss << "Downcast from " << fromCS << " to " << toCS;
        std::string errmsg = oss.str();
        PyErr_SetString(PyExc_TypeError, errmsg.c_str());
        return NULL;
    }

    auto_pyobject oldObj = Unwrap(obj);
    auto_pyobject newObj = PyObject_CallFunctionObjArgs(*caster, *oldObj,
                                                        NULL);

    bool used_to_own = HasOwnership(*oldObj);

    PyObject *result = Wrap(*newObj, !used_to_own);

    int status = PyObject_Not(result);
    switch(status) {
    case 0:
        return result;
    case 1:
    default:
        PyErr_SetString(PyExc_ValueError, "Downcast failed");
        Py_XDECREF(result);
        return NULL;
    }
}

///////////////////////////////////////////////////////////////////////////////

struct CapsuleObject {
    PyObject_HEAD;
    PyObject *capsule;
};

static
void Capsule_dealloc(CapsuleObject* self) {
    Py_XDECREF(self->capsule);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static
int Capsule_init(CapsuleObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *cap;
    if (!PyArg_ParseTuple(args, "O", &cap)) {
        return -1;
    }

    if (!Check(cap)) {
        PyErr_SetString(PyExc_TypeError, "Expected PyCapsule object");
        return -1;
    }

    Py_INCREF(cap);
    self->capsule = cap;

    PyObject* addr2refct = GetAddrRefCt();

    auto_pyobject ptr = GetPointer(self->capsule);
    auto_pyobject refct = PyObject_GetItem(addr2refct, *ptr);
    auto_pyobject inc = PyNumber_InPlaceAdd(*refct, ConstantOne);
    return PyObject_SetItem(addr2refct, *ptr, *inc);
}

static
PyObject* Capsule_getclassname(CapsuleObject* self, void *closure) {
    return GetClassName(self->capsule);
}

static
PyObject* Capsule_getname(CapsuleObject* self, void *closure) {
    return GetName(self->capsule);
}

static
PyObject* Capsule_getpointer(CapsuleObject* self, void *closure) {
    return GetPointer(self->capsule);
}


static
PyObject* Capsule_GetClass(CapsuleObject *self){
    PyObject *pycls = GetClassesDict();
    auto_pyobject key = GetClassName(self->capsule);
    return PyDict_GetItem(pycls, *key);    // borrowed reference
}

static
PyObject* Capsule_get_class(CapsuleObject* self, PyObject* args) {
    PyObject* out = Capsule_GetClass(self);
    Py_XINCREF(out);
    return out;
}

static
PyObject* Capsule_instantiate(CapsuleObject* self, PyObject* args) {
    return PyObject_CallFunctionObjArgs(Capsule_GetClass(self), self, NULL);
}

/// Rotate Right
static unsigned long RotR(unsigned long hash, int offset){
    if (offset == 0) return hash;

    unsigned long out = hash << (sizeof(hash) * 8 - offset);
    out |= hash >> offset;
    return out;
}


/*
This is called everytime an object is returned from LLVM.
It derserves to be optimized to reduce unnecessary Python object allocation.
The following implements a simple hash function that uses XOR and
right-rotation.
*/
static
long Capsule_hash(CapsuleObject *self) {
    const char* name = PyCapsule_GetName(self->capsule);
    void *pointer = PyCapsule_GetPointer(self->capsule, name);

    unsigned long hash = 0xabcd1234 ^ (unsigned long)pointer;

    // The first loop accounts for the different LLVM class name and the
    // length of the name.
    for(const char* p = name; *p != '\0'; ++p) {
        hash ^= *p;
        hash = RotR(hash, 11);
    }

    // The second loop accounts for the pointer identity.
    for(int i = 0; i <sizeof(pointer); ++i) {
        hash ^= ((unsigned char*)&pointer)[i];
        hash = RotR(hash, 11);
    }

    return hash;
}

static
bool Capsule_eq(PyObject *self, PyObject *other) {
    if (PyObject_Type(self) == PyObject_Type(other)) {
        CapsuleObject *a = (CapsuleObject*)self;
        CapsuleObject *b = (CapsuleObject*)other;

        void* pa = PyCapsule_GetPointer(a->capsule,
                                        PyCapsule_GetName(a->capsule));
        void* pb = PyCapsule_GetPointer(b->capsule,
                                        PyCapsule_GetName(b->capsule));
        return pa == pb;
    }
    return false;
}

static
PyObject* Capsule_richcmp(PyObject *a, PyObject *b, int op) {
    bool ret = Capsule_eq(a, b);
    switch(op) {
    case Py_EQ:             break;
    case Py_NE: ret = !ret; break;
    default:
        return Py_NotImplemented;
    }
    if (ret) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyMemberDef Capsule_members[] = {
    {"capsule", T_OBJECT_EX, offsetof(CapsuleObject, capsule), READONLY, "capsule"},
    { NULL },
};

static PyMethodDef Capsule_methods[] = {
    { "get_class", (PyCFunction)Capsule_get_class, METH_NOARGS,
      "Get Capsule class"},
    { "instantiate", (PyCFunction)Capsule_instantiate, METH_NOARGS,
      "create a new instance"},
    { NULL },
};

static PyGetSetDef Capsule_getseters[] = {
    {"classname", (getter)Capsule_getclassname, NULL, "class name", NULL},
    {"name", (getter)Capsule_getname, NULL, "name", NULL},
    {"pointer", (getter)Capsule_getpointer, NULL, "pointer", NULL},
    { NULL },
};

static PyTypeObject CapsuleType = {
#if (PY_MAJOR_VERSION < 3)
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
#else
    PyVarObject_HEAD_INIT(NULL, 0)
#endif
    "_capsule.Capsule",        /*tp_name*/
    sizeof(CapsuleObject),     /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Capsule_dealloc,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    (hashfunc)Capsule_hash,    /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Capsule object",          /* tp_doc */
    0,		                   /* tp_traverse */
    0,		                   /* tp_clear */
    (richcmpfunc)Capsule_richcmp,   /*tp_richcompare */
    0,		                   /* tp_weaklistoffset */
    0,		                   /* tp_iter */
    0,		                   /* tp_iternext */
    Capsule_methods,           /* tp_methods */
    Capsule_members,           /* tp_members */
    Capsule_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Capsule_init,              /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
};


///////////////////////////////////////////////////////////////////////////////


static PyMethodDef core_methods[] = {
#define declmethod(func) { #func , ( PyCFunction )func , METH_VARARGS , NULL }
    declmethod(getName),
    declmethod(getPointer),
    declmethod(check),
    declmethod(getClassName),
    declmethod(unwrap),
    declmethod(wrap),
    declmethod(has_ownership),
    declmethod(downcast),
    { NULL },
#undef declmethod
};

// Module main function, hairy because of py3k port
extern "C" {

#if (PY_MAJOR_VERSION >= 3)
    struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_capsule",
        NULL,
        -1,
        core_methods,
        NULL, NULL, NULL, NULL
    };
#define INITERROR return NULL
    PyObject *
    PyInit__capsule(void)
#else
#define INITERROR return
    PyMODINIT_FUNC
    init_capsule(void)
#endif
    {
#if PY_MAJOR_VERSION >= 3
        PyObject *module = PyModule_Create( &module_def );
#else
        PyObject *module = Py_InitModule("_capsule", core_methods);
#endif
        if (module == NULL){
            INITERROR;
        }

        if (module) {
            CapsuleType.tp_new = PyType_GenericNew;
            if (PyType_Ready(&CapsuleType) < 0) {
                INITERROR;
            }
            Py_INCREF(&CapsuleType);
            PyModule_AddObject(module, "Capsule", (PyObject*)(&CapsuleType));

            ConstantOne = PyInt_FromLong(1);
        }
#if PY_MAJOR_VERSION >= 3
        return module;
#endif
    }
    
} // end extern C
