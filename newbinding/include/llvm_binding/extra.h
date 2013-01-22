#include <Python.h>
#include <llvm/ADT/SmallVector.h>
#include <llvm/Support/raw_ostream.h>

namespace llvm{ 

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

