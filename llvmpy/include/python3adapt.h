#ifndef PYTHON3ADAPT_H
#define PYTHON3ADAPT_H

#if (PY_VERSION_HEX < 0x03000000)

#define PyBytes_Check               PyString_Check
#define PyBytes_Size                PyString_Size
#define PyBytes_AsString            PyString_AsString
#define PyBytes_FromStringAndSize   PyString_FromStringAndSize
#define PyBytes_FromString          PyString_FromString

#else

#define PyString_Check PyUnicode_Check
#define PyString_Size PyUnicode_GET_SIZE
#define PyString_FromStringAndSize PyUnicode_FromStringAndSize
#define PyString_FromString PyUnicode_FromString

#define PyInt_Check PyLong_Check
#define PyInt_FromLong PyLong_FromLong
#define PyInt_AsLong PyLong_AsLong
#define PyInt_AsUnsignedLongMask PyLong_AsUnsignedLongMask
#define PyInt_AsUnsignedLongLongMask PyLong_AsUnsignedLongLongMask

#define PyFile_Check(x) (1)

#if (PY_VERSION_HEX < 0x03030000)
#define PyString_AsString _PyUnicode_AsString
#else
#define PyString_AsString PyUnicode_AsUTF8
#endif

#endif  // (PY_VERSION_HEX < 0x03000000)

#endif  //PYTHON3ADAPT_H
