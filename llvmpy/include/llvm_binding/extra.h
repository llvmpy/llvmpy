#include <Python.h>
#include <llvm/ADT/SmallVector.h>
#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 3
    #include <llvm/IR/Value.h>
    #include <llvm/IR/DerivedTypes.h>
    #include <llvm/IR/Function.h>
    #include <llvm/IR/Module.h>
    #include <llvm/IR/Constants.h>
    #include <llvm/IR/Intrinsics.h>
    #include <llvm/IR/IRBuilder.h>
    #if LLVM_VERSION_MINOR >= 4
        #include <llvm/Support/MemoryObject.h>
        #include <llvm/MC/MCDisassembler.h>
    #endif
#else
    #include <llvm/Value.h>
    #include <llvm/DerivedTypes.h>
    #include <llvm/Function.h>
    #include <llvm/Module.h>
    #include <llvm/Constants.h>
    #include <llvm/Intrinsics.h>
    #include <llvm/IRBuilder.h>
#endif
#include <llvm/Support/raw_ostream.h>
#include <llvm/Support/FormattedStream.h>
#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/DynamicLibrary.h>
#include <llvm/Support/TargetRegistry.h>
#include <llvm/Bitcode/ReaderWriter.h>
#include <llvm/ExecutionEngine/ExecutionEngine.h>
#include <llvm/ExecutionEngine/GenericValue.h>
#include <llvm/Linker.h>
#include <llvm/Analysis/Verifier.h>
#include <llvm/PassRegistry.h>
#include <llvm/Support/Host.h>

#include <llvm/ExecutionEngine/MCJIT.h> // to make MCJIT working

#include "auto_pyobject.h"

namespace extra{
    using namespace llvm;
    
    class raw_svector_ostream_helper: public raw_svector_ostream {
        SmallVectorImpl<char> *SV;
    public:
        static
        raw_svector_ostream_helper* create()
        {
            SmallVectorImpl<char>* sv = new SmallVector<char, 16>();
            return new raw_svector_ostream_helper(sv);
        }

        ~raw_svector_ostream_helper()
        {
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
PyObject* callwrite(PyObject* self, PyObject* arg)
{
    char meth[] = "write";
    char fmt[] = "O";
    return PyObject_CallMethod(self, meth, fmt, arg);
}


static
PyObject* make_raw_ostream_for_printing(PyObject* self, PyObject* args)
{
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
PyObject* make_small_vector_from_types(PyObject* self, PyObject* args)
{
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

static
PyObject* make_small_vector_from_values(PyObject* self, PyObject* args)
{
    using llvm::Value;
    typedef llvm::SmallVector<llvm::Value*, 8> SmallVector_Value;

    SmallVector_Value* SV = new SmallVector_Value;
    Py_ssize_t size = PyTuple_Size(args);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject* cap = PyTuple_GetItem(args, i);
        if (!cap) {
            return NULL;
        }
        Value* value = (Value*)PyCapsule_GetPointer(cap, "llvm::Value");
        if (!value) {
            return NULL;
        }
        SV->push_back(value);
    }
    return pycapsule_new(SV, "llvm::SmallVector<llvm::Value*,8>");
}


static
PyObject* make_small_vector_from_unsigned(PyObject* self, PyObject* args)
{
    using llvm::Value;
    typedef llvm::SmallVector<unsigned, 8> SmallVector_Unsigned;

    SmallVector_Unsigned* SV = new SmallVector_Unsigned;
    Py_ssize_t size = PyTuple_Size(args);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject* item = PyTuple_GetItem(args, i);
        if (!item) {
            return NULL;
        }
        unsigned value = PyLong_AsUnsignedLong(item);
        if (PyErr_Occurred()){
            return NULL;
        }
        SV->push_back(value);
    }
    return pycapsule_new(SV, "llvm::SmallVector<unsigned,8>");
}

static
PyObject* get_llvm_version(PyObject* self, PyObject* args)
{
    return Py_BuildValue("(ii)", LLVM_VERSION_MAJOR, LLVM_VERSION_MINOR);
}

static PyMethodDef extra_methodtable[] = {
    #define method(func) { #func, (PyCFunction)func, METH_VARARGS, NULL }
    method( make_raw_ostream_for_printing ),
    method( make_small_vector_from_types ),
    method( make_small_vector_from_values ),
    method( make_small_vector_from_unsigned ),
    method( get_llvm_version ),
    #undef method
    { NULL }
};


////////////
template<class iterator>
PyObject* iterator_to_pylist_deref(iterator begin, iterator end,
                             const char *capsuleName, const char *className)
{
    PyObject* list = PyList_New(0);
    for(; begin != end; ++begin) {
        PyObject* cap = pycapsule_new(&*begin, capsuleName, className);
        PyList_Append(list, cap);
    }
    return list;
}

template<class iterator>
PyObject* iterator_to_pylist(iterator begin, iterator end,
                             const char *capsuleName, const char *className)
{
    PyObject* list = PyList_New(0);
    for(; begin != end; ++begin) {
        PyObject* cap = pycapsule_new(*begin, capsuleName, className);
        PyList_Append(list, cap);
    }
    return list;
}

template<class iplist>
PyObject* iplist_to_pylist(iplist &IPL, const char * capsuleName,
                           const char* className){
    return iterator_to_pylist_deref(IPL.begin(), IPL.end(), capsuleName,
                                    className);
}

template<class ElemTy>
struct extract {

    template<class VecTy>
    static
    bool from_py_sequence(VecTy& vec, PyObject* seq, const char *capsuleName,
                          bool accept_null=false)
    {
        Py_ssize_t N = PySequence_Size(seq);
        for (Py_ssize_t i = 0; i < N; ++i) {
            auto_pyobject item = PySequence_GetItem(seq, i);
            if (!item) {
                return false;
            }
            if (accept_null && Py_None == *item) {
                vec.push_back(NULL);
            } else {
                auto_pyobject capsule = PyObject_GetAttrString(*item, "_ptr");
                if (!capsule) {
                    return false;
                }
                void* ptr = PyCapsule_GetPointer(*capsule, capsuleName);
                if (!ptr) {
                    return false;
                }
                ElemTy* res = typecast<ElemTy>::from(ptr);
                if (!res) {
                    return false;
                }
                vec.push_back(res);
            }
        }
        return true;
    }

};
//static
//bool string_equal(const char *A, const char *B){
//    for (; *A and *B; ++A, ++B) {
//        if (*A != *B) return false;
//    }
//    return true;
//}

////////////
static
PyObject* Value_use_iterator_to_list(llvm::Value* val)
{
    return iterator_to_pylist(val->use_begin(), val->use_end(),
                              "llvm::Value", "llvm::User");
}

static
PyObject* Function_getArgumentList(llvm::Function* fn)
{
    return iplist_to_pylist(fn->getArgumentList(), "llvm::Value",
                            "llvm::Argument");
}

static
PyObject* Function_getBasicBlockList(llvm::Function* fn)
{
    return iplist_to_pylist(fn->getBasicBlockList(), "llvm::Value",
                            "llvm::BasicBlock");
}

/*
 * errout --- can be any file object
 *
 */
static
llvm::ExecutionEngine* ExecutionEngine_create(
                  llvm::Module* M,
                  bool ForceInterpreter = false,
                  PyObject* errout = 0,
                  llvm::CodeGenOpt::Level OptLevel = llvm::CodeGenOpt::Default,
                  bool 	GVsWithCode = true)
{
    using namespace llvm;
    std::string ErrorStr;
    ExecutionEngine *ee = ExecutionEngine::create(M, ForceInterpreter,
                                                  &ErrorStr, OptLevel,
                                                  GVsWithCode);
    auto_pyobject buf = PyBytes_FromString(ErrorStr.c_str());
    if (errout && NULL == callwrite(errout, *buf)){
        return NULL;
    }

//    PyFile_WriteString(ErrorStr.c_str(), errout);
    return ee;
}

/*
 * errout --- can be any file object
 *
 */
static
llvm::ExecutionEngine* ExecutionEngine_createJIT(
                     llvm::Module* M,
                     PyObject* errout = 0,
                     llvm::JITMemoryManager* JMM = 0,
                     llvm::CodeGenOpt::Level OL = llvm::CodeGenOpt::Default,
                     bool GCsWithCode = true,
                     llvm::Reloc::Model RM = llvm::Reloc::Default,
                     llvm::CodeModel::Model CMM = llvm::CodeModel::JITDefault)
{
    using namespace llvm;
    std::string ErrorStr;
    ExecutionEngine *ee = ExecutionEngine::createJIT(M, &ErrorStr, JMM, OL,
                                                     GCsWithCode, RM, CMM);
    auto_pyobject buf = PyBytes_FromString(ErrorStr.c_str());
    if (errout && NULL == callwrite(errout, *buf)){
        return NULL;
    }
//    PyFile_WriteString(ErrorStr.c_str(), errout);
    return ee;
}

static
llvm::GenericValue* GenericValue_CreateInt(llvm::Type* Ty, unsigned long long N,
                                           bool IsSigned)
{
    // Shamelessly copied from LLVM
    llvm::GenericValue *GenVal = new llvm::GenericValue();
    GenVal->IntVal = llvm::APInt(Ty->getIntegerBitWidth(), N, IsSigned);
    return GenVal;
}

static
llvm::GenericValue* GenericValue_CreateFloat(float Val)
{
    llvm::GenericValue *GenVal = new llvm::GenericValue();
    GenVal->FloatVal = Val;
    return GenVal;
}

static
llvm::GenericValue* GenericValue_CreateDouble(double Val)
{
    llvm::GenericValue *GenVal = new llvm::GenericValue();
    GenVal->DoubleVal = Val;
    return GenVal;
}

static
llvm::GenericValue* GenericValue_CreatePointer(void * Ptr)
{
    llvm::GenericValue *GenVal = new llvm::GenericValue();
    GenVal->PointerVal = Ptr;
    return GenVal;
}

static
unsigned GenericValue_ValueIntWidth(llvm::GenericValue *GenValRef)
{
    return GenValRef->IntVal.getBitWidth();
}

static
unsigned long long GenericValue_ToUnsignedInt(llvm::GenericValue* GenVal)
{
    return GenVal->IntVal.getZExtValue();
}


static
long long GenericValue_ToSignedInt(llvm::GenericValue* GenVal)
{
    return GenVal->IntVal.getSExtValue();
}

static
void* GenericValue_ToPointer(llvm::GenericValue* GenVal)
{
    return GenVal->PointerVal;
}

static
double GenericValue_ToFloat(llvm::GenericValue* GenVal, llvm::Type* Ty)
{
    switch (Ty->getTypeID()) {
        case llvm::Type::FloatTyID:
            return GenVal->FloatVal;
        default:
            // Behavior undefined if type is not a float or a double
            return GenVal->DoubleVal;
    }
}

static
PyObject* ExecutionEngine_RunFunction(llvm::ExecutionEngine* EE,
                                      llvm::Function* Fn, PyObject* Args)
{
    using namespace llvm;
    const char * GVN = "llvm::GenericValue";
    if (!PyTuple_Check(Args)) {
        PyErr_SetString(PyExc_TypeError, "Expect a tuple of args.");
        return NULL;
    }
    std::vector<GenericValue> vec_args;

    Py_ssize_t nargs = PyTuple_Size(Args);
    vec_args.reserve(nargs);
    for (Py_ssize_t i = 0; i < nargs; ++i) {
        PyObject* obj = PyTuple_GetItem(Args, i);
        if (!obj) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to index into args?");
            return NULL;
        }
        
        GenericValue* gv = static_cast<GenericValue*>(
                              PyCapsule_GetPointer(obj, GVN));

        if (!gv) {
            return NULL;
        }
        vec_args.push_back(*gv);
    }

    GenericValue ret = EE->runFunction(Fn, vec_args);
    return pycapsule_new(new GenericValue(ret), GVN);
}

// FIXME
//static
//PyObject* EngineBuilder_setErrorStr(llvm::EngineBuilder* eb, PyObject* fileobj)
//{
//
//    std::string buffer;
//    eb->setErrorStr(&buffer);
//
//    if (-1 == PyFile_WriteString(buffer.c_str(), fileobj)) {
//        return NULL;
//    }
//
//    return pycapsule_new(eb, "llvm::EngineBuilder");
//}

static
PyObject* EngineBuilder_setMAttrs(llvm::EngineBuilder* eb,
                                  PyObject* strlist)
{
    if (!PyList_Check(strlist)) {
        PyErr_SetString(PyExc_TypeError, "Expecting a list of string.");
        return NULL;
    }
    std::vector<const char*> tmp;
    const Py_ssize_t N = PyList_Size(strlist);
    tmp.reserve(N);
    for (Py_ssize_t i = 0; i < N; ++i) {
        const char * elem = PyString_AsString(PyList_GetItem(strlist, i));
        if (!elem) {
            return NULL;
        }
        tmp.push_back(elem);
    }
    eb->setMAttrs(tmp);
    return pycapsule_new(eb, "llvm::EngineBuilder");
}

static
PyObject* EngineBuilder_selectTarget(llvm::EngineBuilder* eb,
                                     const llvm::Triple& TargetTriple,
                                     llvm::StringRef MArch,
                                     llvm::StringRef MCPU,
                                     PyObject* strlist)
{
    const Py_ssize_t N = PySequence_Size(strlist);
    llvm::SmallVector<std::string, 8> MAttrs;
    MAttrs.reserve(N);
    for (Py_ssize_t i = 0; i < N; ++i) {
        PyObject* str = PySequence_GetItem(strlist, i);
        const char * cp = PyString_AsString(str);
        if (!cp) {
            Py_DECREF(str);
            return NULL;
        }
        MAttrs.push_back(cp);
        Py_DECREF(str);
    }
    eb->selectTarget(TargetTriple, MArch, MCPU, MAttrs);
    return pycapsule_new(eb, "llvm::EngineBuilder");
}


static
PyObject* llvm_ParseBitCodeFile(llvm::StringRef Buf, llvm::LLVMContext& Ctx,
                                PyObject* FObj=NULL)
{
    using namespace llvm;
    MemoryBuffer* MB = MemoryBuffer::getMemBuffer(Buf);
    Module* M;
    if (FObj) {
        std::string ErrStr;
        M = ParseBitcodeFile(MB, Ctx, &ErrStr);
        auto_pyobject buf = PyBytes_FromString(ErrStr.c_str());
        if (NULL == callwrite(FObj, *buf)){
            return NULL;
        }
//        if (-1 == PyFile_WriteString(ErrStr.c_str(), FObj)) {
//            return NULL;
//        }
    } else {
        M = ParseBitcodeFile(MB, Ctx);
    }
    delete MB;
    return pycapsule_new(M, "llvm::Module");
}


static
PyObject* llvm_WriteBitcodeToFile(const llvm::Module *M, PyObject* FObj)
{
    using namespace llvm;
    llvm::SmallVector<char, 32> sv;
    llvm::raw_svector_ostream rso(sv);
    llvm::WriteBitcodeToFile(M, rso);
    rso.flush();
    StringRef ref = rso.str();
    auto_pyobject buf = PyBytes_FromStringAndSize(ref.data(), ref.size());
    return callwrite(FObj, *buf);
}

static
PyObject* llvm_getBitcodeTargetTriple(llvm::StringRef Buf,
                                      llvm::LLVMContext& Ctx,
                                      PyObject* FObj = NULL)
{
    using namespace llvm;
    MemoryBuffer* MB = MemoryBuffer::getMemBuffer(Buf);
    std::string Triple;
    if (FObj) {
        std::string ErrStr;
        Triple = getBitcodeTargetTriple(MB, Ctx, &ErrStr);
        auto_pyobject buf = PyBytes_FromString(ErrStr.c_str());
        if (NULL == callwrite(FObj, *buf)){
            return NULL;
        }
//        if (-1 == PyFile_WriteString(ErrStr.c_str(), FObj)) {
//            return NULL;
//        }
    } else {
        Triple = getBitcodeTargetTriple(MB, Ctx);
    }
    delete MB;
    return PyString_FromString(Triple.c_str());
}

static
PyObject* TargetMachine_addPassesToEmitFile(
                                llvm::TargetMachine *TM,
                                llvm::PassManagerBase & PM,
                                PyObject* Out,
                                llvm::TargetMachine::CodeGenFileType FTy,
                                bool disableVerify=true)
{
    using namespace llvm;
    llvm::SmallVector<char, 32> sv;
    raw_svector_ostream rso(sv);
    formatted_raw_ostream fso(rso);
    fso.flush();
    bool status = TM->addPassesToEmitFile(PM, fso, FTy, disableVerify);
    if (status) {
        StringRef sr = rso.str();
        PyObject* buf = PyString_FromStringAndSize(sr.data(), sr.size());
        if (!buf) {
            return NULL;
        }
        if (-1 == PyFile_WriteObject(buf, Out, Py_PRINT_RAW)){
            return NULL;
        }
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static
PyObject* Constant_getIntegerValue(llvm::Type* Ty, PyObject* pyint)
{
    using namespace llvm;
    if (!Ty->isIntegerTy()) {
        PyErr_SetString(PyExc_ValueError, "Type should be of integer type.");
        return NULL;
    }
    unsigned width = Ty->getIntegerBitWidth();
    if (width > sizeof(unsigned long long)*8) {
        PyErr_SetString(PyExc_ValueError, "Integer value is too large.");
    }
    Constant* K;
    if (PyLong_Check(pyint)){
        APInt apint(width, PyLong_AsLongLong(pyint), true);
        K = Constant::getIntegerValue(Ty, apint);
    } else {
        APInt apint(width, PyInt_AsLong(pyint), true);
        K = Constant::getIntegerValue(Ty, apint);
    }
    return pycapsule_new(K, "llvm::Value", "llvm::Constant");
}


static
PyObject* Linker_LinkInModule(llvm::Linker* Linker,
                               llvm::Module* Mod,
                               PyObject* ErrMsg)
{
    std::string errmsg;
#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 3
    bool failed = Linker->linkInModule(Mod, &errmsg);
#else
    bool failed = Linker->LinkInModule(Mod, &errmsg);
#endif
    if (! failed) {
        Py_RETURN_FALSE;
    } else {
    
        auto_pyobject buf = PyBytes_FromString(errmsg.c_str());
        if (NULL == callwrite(ErrMsg, *buf)){
            return NULL;
        }
        Py_RETURN_TRUE;
    }
}

static
PyObject* Linker_LinkModules(llvm::Module* Dest,
                             llvm::Module* Src,
                             unsigned Mode,
                             PyObject* ErrMsg)
{
    std::string errmsg;
    bool failed = llvm::Linker::LinkModules(Dest, Src, Mode, &errmsg);
    if (! failed) {
        Py_RETURN_FALSE;
    } else {
        auto_pyobject buf = PyBytes_FromString(errmsg.c_str());
        if (NULL == callwrite(ErrMsg, *buf)){
            return NULL;
        }
//        if (-1 == PyFile_WriteString(errmsg.c_str(), ErrMsg)) {
//            return NULL;
//        }
        Py_RETURN_TRUE;
    }
}

static
PyObject* StructType_setBody(llvm::StructType* Self,
                             PyObject* Elems,
                             bool isPacked=false)
{
    using namespace llvm;
    std::vector<Type*> elements;
    extract<Type>::from_py_sequence(elements, Elems, "llvm::Type");
    Self->setBody(elements, isPacked);
    Py_RETURN_NONE;
}

static
PyObject* StructType_get(llvm::LLVMContext& Cxt,
                         PyObject* Elems,
                         bool isPacked=false)
{
    using namespace llvm;
    std::vector<Type*> elements;
    extract<Type>::from_py_sequence(elements, Elems, "llvm::Type");
    StructType *sty = StructType::get(Cxt, elements, isPacked);
    return pycapsule_new(sty, "llvm::Type", "llvm::StructType");
}

static
PyObject* Module_list_globals(llvm::Module* Mod)
{
    return iplist_to_pylist(Mod->getGlobalList(),
                            "llvm::Value", "llvm::GlobalVariable");
}

static
PyObject* Module_list_functions(llvm::Module* Mod)
{
    return iplist_to_pylist(Mod->getFunctionList(),
                            "llvm::Value", "llvm::Function");
}

static
PyObject* Module_list_named_metadata(llvm::Module* Mod)
{
    return iplist_to_pylist(Mod->getFunctionList(),
                            "llvm::NamedMDNode", "llvm::NamedMDNode");

}

static
PyObject* llvm_verifyModule(const llvm::Module& Fn,
                              llvm::VerifierFailureAction Action,
                              PyObject* ErrMsg)
{
    std::string errmsg;
    bool failed = llvm::verifyModule(Fn, Action, &errmsg);

    if (failed) {
        auto_pyobject buf = PyBytes_FromString(errmsg.c_str());
        if (NULL == callwrite(ErrMsg, *buf)){
            return NULL;
        }

//        if (-1 == PyFile_WriteString(errmsg.c_str(), ErrMsg)) {
//            return NULL;
//        }
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static
PyObject* ConstantArray_get(llvm::ArrayType* Ty, PyObject* Consts)
{
    using namespace llvm;

    std::vector<Constant*> vec_consts;
    bool ok = extract<Constant>::from_py_sequence(vec_consts, Consts,
                                                  "llvm::Value");
    if (! ok) return NULL;
    Constant* ary = ConstantArray::get(Ty, vec_consts);
    return pycapsule_new(ary, "llvm::Value", "llvm::Constant");
}

static
PyObject* ConstantStruct_get(llvm::StructType* Ty, PyObject* Elems)
{
    using namespace llvm;

    std::vector<Constant*> vec_consts;
    bool ok = extract<Constant>::from_py_sequence(vec_consts, Elems,
                                                  "llvm::Value");
    if (! ok) return NULL;
    Constant* ary = ConstantStruct::get(Ty, vec_consts);
    return pycapsule_new(ary, "llvm::Value", "llvm::Constant");
}

static
PyObject* ConstantStruct_getAnon(PyObject* Elems,
                                            bool isPacked=false)
{
    using namespace llvm;

    std::vector<Constant*> vec_consts;
    bool ok = extract<Constant>::from_py_sequence(vec_consts, Elems,
                                                  "llvm::Value");
    if (! ok) return NULL;
    Constant* ary = ConstantStruct::getAnon(vec_consts, isPacked);
    return pycapsule_new(ary, "llvm::Value", "llvm::Constant");
}

static
PyObject* ConstantVector_get(PyObject* Elems)
{
    using namespace llvm;

    std::vector<Constant*> vec_consts;
    bool ok = extract<Constant>::from_py_sequence(vec_consts, Elems,
                                                  "llvm::Value");
    if (! ok) return NULL;
    Constant* ary = ConstantVector::get(vec_consts);
    return pycapsule_new(ary, "llvm::Value", "llvm::Constant");
}

static
PyObject* Intrinsic_getDeclaration(llvm::Module* Mod,
                                   unsigned ID,
                                   PyObject* Types=NULL)
{
    using namespace llvm;
    Function* Fn = NULL;
    if (Types) {
        std::vector<Type*> types;
        bool ok = extract<Type>::from_py_sequence(types, Types, "llvm::Type");
        if (!ok) return NULL;
        Fn = Intrinsic::getDeclaration(Mod, (Intrinsic::ID)ID, types);
    } else {
        Fn = Intrinsic::getDeclaration(Mod, (Intrinsic::ID)ID);
    }
    return pycapsule_new(Fn, "llvm::Value", "llvm::Function");
}

static
PyObject* MDNode_get(llvm::LLVMContext &Cxt, PyObject* Vals)
{
    std::vector<llvm::Value*> vals;
    bool accept_null = true;
    bool ok = extract<llvm::Value>::from_py_sequence(vals, Vals, "llvm::Value",
                                                     accept_null);
    if (! ok) return NULL;
    llvm::MDNode* md = llvm::MDNode::get(Cxt, vals);
    return pycapsule_new(md, "llvm::Value", "llvm::MDNode");
}


static
PyObject* BasicBlock_getInstList(llvm::BasicBlock* BB)
{
    return iplist_to_pylist(BB->getInstList(),
                            "llvm::Value",
                            "llvm::Instruction");
}

static
PyObject* IRBuilder_CreateAggregateRet(llvm::IRBuilder<>* builder,
                                       PyObject* Vals,
                                       unsigned N)
{
    using namespace llvm;
    std::vector<Value*> vec_values;
    bool ok = extract<Value>::from_py_sequence(vec_values, Vals, "llvm::Value");
    if (! ok) return NULL;
    Value** ptr_values = &vec_values[0];
    ReturnInst* inst = builder->CreateAggregateRet(ptr_values, N);
    return pycapsule_new(inst, "llvm::Value", "llvm::ReturnInst");
}

static
PyObject* DynamicLibrary_LoadLibraryPermanently(const char * Filename,
                                                PyObject* ErrMsg = 0)
{
    using namespace llvm::sys;
    bool failed;
    if (ErrMsg) {
        std::string errmsg;
        failed = DynamicLibrary::LoadLibraryPermanently(Filename, &errmsg);
        if (failed) {
            auto_pyobject buf = PyBytes_FromString(errmsg.c_str());
            if (NULL == callwrite(ErrMsg, *buf)){
                return NULL;
            }
//            if (-1 == PyFile_WriteString(errmsg.c_str(), ErrMsg)) {
//                return NULL;
//            }
        }
    } else {
        failed = DynamicLibrary::LoadLibraryPermanently(Filename);
    }

    if (failed) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

class PassRegistryEnumerator : public llvm::PassRegistrationListener{
public:
    PyObject* List;
public:
    PassRegistryEnumerator(PyObject* list) : List(list) { }

    inline virtual void passEnumerate(const llvm::PassInfo * pass_info){
        PyObject* passArg = PyString_FromString(pass_info->getPassArgument());
        PyObject* passName = PyString_FromString(pass_info->getPassName());
        PyList_Append(List, Py_BuildValue("(OO)", passArg, passName));
    }
};

static
PyObject* PassRegistry_enumerate(llvm::PassRegistry* PR)
{
    using namespace llvm;
    PassRegistryEnumerator PRE(PyList_New(0));
    PR->enumerateWith(&PRE);
    return PRE.List;
}

static
PyObject* TargetRegistry_lookupTarget(const std::string &Triple,
                                      PyObject* Error)
{
    using namespace llvm;
    std::string error;
    const Target* target = TargetRegistry::lookupTarget(Triple, error);
    if (!target) {
//        PyFile_WriteString(error.c_str(), Error);
        auto_pyobject buf = PyBytes_FromString(error.c_str());
        if (NULL == callwrite(Error, *buf)){
            return NULL;
        }

        Py_RETURN_NONE;
    } else {
        return pycapsule_new(const_cast<Target*>(target), "llvm::Target");
    }
}


static
PyObject* TargetRegistry_lookupTarget(const std::string &Arch,
                                      llvm::Triple &Triple,
                                      PyObject* Error)
{
    using namespace llvm;
    std::string error;
    const Target* target = TargetRegistry::lookupTarget(Arch, Triple, error);
    if (!target) {
//        PyFile_WriteString(error.c_str(), Error);
        auto_pyobject buf = PyBytes_FromString(error.c_str());
        if (NULL == callwrite(Error, *buf)){
            return NULL;
        }

        Py_RETURN_NONE;
    } else {
        return pycapsule_new(const_cast<Target*>(target), "llvm::Target");
    }
}

static
PyObject* TargetRegistry_getClosestTargetForJIT(PyObject* Error)
{
    using namespace llvm;
    std::string error;
    const Target* target = TargetRegistry::getClosestTargetForJIT(error);
    if (!target) {
        auto_pyobject buf = PyBytes_FromString(error.c_str());
        if (NULL == callwrite(Error, *buf)){
            return NULL;
        }

//        PyFile_WriteString(error.c_str(), Error);
        Py_RETURN_NONE;
    } else {
        return pycapsule_new(const_cast<Target*>(target), "llvm::Target");
    }

}

static
PyObject* TargetRegistry_targets_list()
{
    using namespace llvm;

    return iterator_to_pylist_deref<TargetRegistry::iterator>(
                  TargetRegistry::begin(), TargetRegistry::end(),
                  "llvm::Target", "llvm::Target");
}

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 4
static
PyObject* MemoryObject_readBytes(const llvm::MemoryObject *mobj,
                                 uint64_t addr,
                                 uint64_t size
                                 )
{
    int status;
    uint8_t *bytes;
    PyObject* po;

    if(size < 1)
        goto fail;

    bytes = new uint8_t[size];
    if(bytes == NULL)
        goto fail;

    status = mobj->readBytes(addr, size, bytes);
    if(status != 0) {
        delete bytes;
        goto fail;
    }

    po = PyBytes_FromStringAndSize((const char *) bytes, size);
    delete bytes;

    return po;
fail:
    Py_RETURN_NONE;
}

static
PyObject* MCDisassembler_getInstruction(llvm::MCDisassembler *disasm, 
                                        llvm::MCInst &instr,
                                        const llvm::MemoryObject &region,
                                        uint64_t address
                                        )
{
    uint64_t size;
    llvm::MCDisassembler::DecodeStatus status;

    size = 0;
    status = disasm->getInstruction(instr, size, region, address, 
                                    llvm::nulls(), llvm::nulls());
    return Py_BuildValue("(i,i)", int(status), size);
}

#endif /* llvm >= 3.4 */

static
PyObject* llvm_sys_getHostCPUFeatures(PyObject* Features)
{
    using namespace llvm::sys;
    using namespace llvm;
    typedef StringMap<bool>::iterator iterator;
    StringMap<bool> features;
    bool ok = getHostCPUFeatures(features);
    if (ok) {
        for (iterator it = features.begin(); it != features.end(); ++it) {
            const char *key = it->getKey().data();
            PyObject *val = it->getValue() ? Py_True : Py_False;
            Py_INCREF(val);
            if (-1 == PyDict_SetItemString(Features, key, val)) {
                return NULL;
            }
        }
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 3
static
PyObject* llvm_sys_isLittleEndianHost()
{
    if (llvm::sys::IsLittleEndianHost)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static
PyObject* llvm_sys_isBigEndianHost()
{
    if (llvm::sys::IsBigEndianHost)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
#endif 

