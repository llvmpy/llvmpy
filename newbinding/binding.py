import logging
import re
from utils import *

logger = logging.getLogger(__name__)

_py2capi_fmtmap = {
    str: 's#',
}

NULL = 'NULL'

_symbols = set()

def new_symbol(name):
    if name in _symbols:
        ct = 1
        orig = name
        while name in _symbols:
            name = '%s%d' % (orig, ct)
            ct += 1
    _symbols.add(name)
    return name

def parse_arguments(println, var, *args):
    typecodes = []
    holders = []
    argvals = []
    for arg in args:
        typecodes.append(arg.format)
        val = declare(println, 'PyObject*')
        argvals.append(val)
        holders.append('&' + val)

    items = [var, '"%s"' % (''.join(typecodes))] + holders
    println('if(!PyArg_ParseTuple(%s)) return NULL;' % ', '.join(items))

    # unwrap
    unwrapped = []
    for arg, val in zip(args, argvals):
        unwrapped.append(arg.unwrap(println, val))

    return unwrapped

_re_mangle_pattern = re.compile(r'[ _<>\*&]')

def mangle(name):
    def repl(m):
        s = m.group(0)
        if s in '<>*&':
            return ''
        elif s in ' ':
            return '_'
        elif s in '_':
            return '__'
        else:
            assert False
    name = _re_mangle_pattern.sub(repl, name)
    return name.replace('::', '_')

def pycapsule_new(println, ptr, name, clsname, dtor=NULL):
    # build capsule
    name_soften = mangle(name)
    var = new_symbol('pycap_%s' % name_soften)
    fmt = 'PyObject* %(var)s = PyCapsule_New(%(ptr)s, "%(name)s", %(dtor)s);'
    println(fmt % locals())

    println('if (!%(var)s) return NULL;' % locals())

    # build context
    fmt = 'new CapsuleContext("%(clsname)s")'
    context = declare(println, 'CapsuleContext*', fmt % locals())

    fmt = 'PyCapsule_SetContext(%(var)s, (void*)%(context)s)'
    err = declare(println, 'int', fmt % locals())

    println('if (%(err)s) return NULL;' % locals())
    return var


def declare(println, typ, init=None):
    typ_soften = mangle(typ)
    var = new_symbol('var_%s' % typ_soften)
    if init is None:
        println('%(typ)s %(var)s;' % locals())
    else:
        println('%(typ)s %(var)s = %(init)s;' % locals())
    return var


def return_value(println, var):
    println('return %(var)s;' % locals())


def return_none(println):
    println('Py_RETURN_NONE;')


def die_if_null(println, var):
    println('if (!%(var)s) return NULL;' % locals())


class Binding(object):
    __rank_global = 0
    def __init__(self):
        self.rank = Binding.__rank_global
        Binding.__rank_global += 1
        self.include = set()

    def compile(self, name, println):
        raise NotImplementedError(type(self))

class Ref(object):
    def __init__(self, elem):
        self.element = elem

    @property
    def fullname(self):
        return '%s&' % self.element.fullname

    @property
    def capsule_name(self):
        return self.element.capsule_name

    @property
    def pointer(self):
        return self.element.pointer

    def as_pointer(self, println, var):
        init = '&%s' % (var)
        casted = declare(println, self.pointer, init)
        return casted

    @property
    def format(self):
        return 'O'

    def unwrap(self, println, var):
        ptr = self.element.unwrap(println, var)
        return declare(println, self.fullname, '*%s' % ptr)

    def wrap(self, println, var):
        return self.element.wrap(println, self.as_pointer(println, var))


class Pointer(object):
    def __init__(self, elem):
        self.element = elem

    @property
    def fullname(self):
        return '%s*' % self.element.fullname

    @property
    def capsule_name(self):
        return self.element.capsule_name

    @property
    def pointer(self):
        return self.element.pointer

    @property
    def format(self):
        return 'O'

    def unwrap(self, println, var):
        ret = declare(println, self.fullname)
        println2 = indent_println(println)
        println('if (%(var)s == Py_None) {' % locals())
        println2('%(ret)s = NULL;' % locals())
        println('} else {')
        ptr = self.element.unwrap(println2, var)
        println2('%(ret)s = %(ptr)s;' % locals())
        println('}')
        return ret

    def wrap(self, println, var):
        return self.element.wrap(println, var)


class BuiltinType(object):
    def __init__(self, name):
        self.name = name
        self.Ref = Ref(self)
        self.Pointer = Pointer(self)

    @property
    def fullname(self):
        return self.name

    @property
    def capsule_name(self):
        return self.fullname

    def To(self, pytype):
        return Wrapper(self, pytype)

    def From(self, pytype):
        return Unwrapper(self, pytype)

Void = BuiltinType('void')
Bool = BuiltinType('bool')
Unsigned = BuiltinType('unsigned')
ConstStdString = BuiltinType('const std::string')

class PyObjectImpl(object):
    name = 'PyObject*'
    fullname = name
    format = 'O'

    def unwrap(self, println, var):
        return var

PyObject = PyObjectImpl()

class Unwrapper(object):
    def __init__(self, cls, pytype):
        self.cls = cls
        self.pytype = pytype

    @property
    def fullname(self):
        return str(self.pytype)

    @property
    def format(self):
        return 'O'

    def unwrap(self, println, var):
        out = declare(println, self.cls.fullname)
        conv = 'py_%s_to' % (self.pytype.__name__)
        status = '%(conv)s(%(var)s, %(out)s)' % locals()
        println('if (!%(status)s) return NULL;' % locals())
        return out


class Wrapper(object):
    def __init__(self, cls, pytype):
        self.cls = cls
        self.pytype = pytype

    @property
    def fullname(self):
        return self.cls.fullname

    def wrap(self, println, var):
        conv = 'py_%s_from' % (self.pytype.__name__)
        func = '%(conv)s(%(var)s)' % locals()
        out = declare(println, 'PyObject*', func)
        println('if (!%(out)s) return NULL;' % locals())
        return out

class Enum(Binding):
    def __init__(self, ns, *values):
        super(Enum, self).__init__()
        self.values = values
        self.ns = ns
        self.name = None

    def compile(self, name, println):
        self.name = self.name or name

    @property
    def fullname(self):
        return '::'.join([self.ns, self.name])

class ClassEnum(Enum):
    def __init__(self, cls, *values):
        super(ClassEnum, self).__init__(None, *values)
        self.cls = cls
        self.cls.enums.append(self)

    def compile(self, name, println):
        self.ns = self.cls.fullname
        super(ClassEnum, self).compile(name, println)

    def wrap(self, println, var):
        println2 = indent_println(println)
        ret = declare(println, 'PyObject*', NULL)
        println('switch(%s) { ' % var)
        for v in self.values:
            println('case %s::%s:' % (self.ns, v))
            println2('%(ret)s = PyString_FromString("%(v)s");' % locals())
            println2('break;')
        else:
            println('default:')
            println2('PyErr_SetString(PyExc_TypeError, "Invalid enum: %s");' %
                     v)
            println2('return NULL;')
        println('}')
        return ret

    def unwrap(self, println, var):
        pass


class Class(Binding):
    def __init__(self, ns):
        super(Class, self).__init__()
        self.ctor = None
        self.Ref = Ref(self)
        self.Pointer = Pointer(self)
        self.Subclass = lambda: Subclass(self)
        self.Enum = lambda *v: ClassEnum(self, *v)
        self.enums = []
        self.ns = ns
        self.methods = []
        self.name = None

    def To(self, pytype):
        return Wrapper(self, pytype)

    def From(self, pytype):
        return Unwrapper(self, pytype)

    def new(self, *args):
        method = Constructor(self, self.Pointer, *args)
        self.methods.append(method)
        return method

    def delete(self):
        method = Destructor(self, Void, self.Pointer)
        self.methods.append(method)
        return method

    def method(self, return_type, *args):
        method = Method(self, return_type, self.Pointer, *args)
        self.methods.append(method)
        return method

    def staticmethod(self, return_type, *args):
        sm = StaticMethod(self, return_type, *args)
        self.methods.append(sm)
        return sm

    def multimethod(self, *signatures):
        mm = MultiMethod(self, signatures)
        self.methods.append(mm)
        return mm

    def staticmultimethod(self, *signatures):
        smm = StaticMultiMethod(self, signatures)
        self.methods.append(smm)
        return smm
    
    def compile(self, name, println):
        # set name
        self.name = self.name or name

    @property
    def capsule_name(self):
        return self.fullname

    @property
    def pointer(self):
        return '%s*' % self.fullname

    @property
    def fullname(self):
        return '::'.join([self.ns, self.name])

    @property
    def mangled_name(self):
        return mangle(self.fullname)

    @property
    def format(self):
        return 'O'

    def unwrap(self, println, var):
        typ = self.pointer
        elty = self.fullname
        cap = self.capsule_name
        capptr = 'PyCapsule_GetPointer(%(var)s, "%(cap)s")' % locals()
        ptr = declare(println, 'void*', capptr)
        unwrapped = 'typecast<%(elty)s>::from(%(ptr)s)' % locals()
        var = declare(println, typ, unwrapped)
        println('if (!%(var)s) {' % locals())
        println2 = indent_println(println)
        println2('PyErr_SetString(PyExc_TypeError, "Invalid cast");')
        println2('return NULL;')
        println('}')
        die_if_null(println, var)
        return var

    def wrap(self, println, var):
         return pycapsule_new(println, var, self.capsule_name, self.fullname)

class Subclass(Class):
    def __init__(self, parent):
        super(Subclass, self).__init__(parent.ns)
        self.parent = parent
        self.ns = self.parent.ns

    @property
    def capsule_name(self):
        return self.parent.capsule_name

class Function(Binding):
    def __init__(self, ns, return_type, *args):
        super(Function, self).__init__()
        self.return_type = return_type
        self.args = args
        self.ns = ns
        self.name = None

    def compile(self, name, println):
        # set name
        self.name = self.name or name
        # generate wrapper
        println('static')
        println('PyObject*')
        println('%(name)s(PyObject* self, PyObject* args)' % locals())
        println('{')
        self.compile_body(indent_println(println))
        println('}')

    def compile_body(self, println):
        args = parse_arguments(println, 'args', *self.args)
        call = '%s(%s)' % (self.fullname, ', '.join(args))
        if self.return_type is not Void:
            callres = declare(println, self.return_type.fullname, call)
            pycap = self.return_type.wrap(println, callres)
            return_value(println, pycap)
        else:
            println('%s;' % call)
            return_none(println)


    @property
    def fullname(self):
        return '::'.join([self.ns, self.name])

class Method(Binding):
    def __init__(self, cls, return_type, *args):
        super(Method, self).__init__()
        self.cls = cls
        self.return_type = return_type
        self.args = args
        self.name = None
        self._realname = None

    def compile(self, name, println):
        # set name
        self.name = self.name or name
        # generate wrapper
        println('static')
        println('PyObject*')
        mangled = self.mangled_name
        println('%(mangled)s(PyObject* self, PyObject* args)' % locals())
        println('{')
        self.compile_body(indent_println(println))
        println('}')
    
    def compile_body(self, println):
        args = parse_arguments(println, 'args', *self.args)
        this = args[0]
        args = ', '.join(args[1:])
        name = self.realname
        call = '%(this)s->%(name)s(%(args)s)' % locals()
        if self.return_type is not Void:
            obj = declare(println, self.return_type.fullname, call)
            ret = self.return_type.wrap(println, obj)
            return_value(println, ret)
        else:
            println('%s;' % call)
            return_none(println)

    @property
    def fullname(self):
        return '::'.join([self.cls.fullname, self.name])

    @property
    def realname(self):
        if not self._realname:
            return self.name
        else:
            return self._realname

    @realname.setter
    def realname(self, v):
        self._realname = v


    @property
    def mangled_name(self):
        return mangle(self.fullname)

class MultiMethod(Binding):
    '''Can only differs by the number of arguments.
    '''
    def __init__(self, cls, signatures):
        super(MultiMethod, self).__init__()
        nargs = set()
        for sig in signatures:
            n = len(sig)
            if n in nargs:
                raise TypeError("MultiMethod only supports overloaded version"
                                "with different number of arguments")
            nargs.add(n)
        self.cls = cls
        self.signatures = signatures
        self.name = None

    def compile(self, name, println):
        # set name
        self.name = self.name or name
        # generate wrapper
        println('static')
        println('PyObject*')
        mangled = self.mangled_name
        println('%(mangled)s(PyObject* self, PyObject* args)' % locals())
        println('{')
        println2 = indent_println(println)
        nargs = declare(println2, 'Py_ssize_t', 'PyTuple_Size(args)')
        for sig in self.signatures:
            expect = len(sig)
            println2('if (%(nargs)s == %(expect)d) {' % locals())
            method = Method(self.cls, sig[0], self.cls.Pointer, *sig[1:])
            method.name = self.name
            method.compile_body(indent_println(println2))
            println2('}')
        println2('PyErr_SetString(PyExc_TypeError, "Wrong # of args");')
        println2('return NULL;')
        println('}')

    @property
    def fullname(self):
        return '::'.join([self.cls.fullname, self.name])

    @property
    def mangled_name(self):
        return mangle(self.fullname)

class StaticMethod(Method):
    def compile_body(self, println):
        args = parse_arguments(println, 'args', *self.args)
        args = ', '.join(args)
        fullname = self.fullname
        call = '%(fullname)s(%(args)s)' % locals()
        if self.return_type is not Void:
            obj = declare(println, self.return_type.fullname, call)
            ret = self.return_type.wrap(println, obj)
            return_value(println, ret)
        else:
            println('%s;' % call)
            return_none(println)

class StaticMultiMethod(Binding):
    '''Can only differs by the number of arguments.
        '''
    def __init__(self, cls, signatures):
        super(StaticMultiMethod, self).__init__()
        nargs = set()
        for sig in signatures:
            n = len(sig)
            if n in nargs:
                raise TypeError("StaticMultiMethod only supports overloaded "
                                "version with different number of arguments")
            nargs.add(n)
        self.cls = cls
        self.signatures = signatures
        self.name = None


    def compile(self, name, println):
        # set name
        self.name = self.name or name
        # generate wrapper
        println('static')
        println('PyObject*')
        mangled = self.mangled_name
        println('%(mangled)s(PyObject* self, PyObject* args)' % locals())
        println('{')
        println2 = indent_println(println)
        nargs = declare(println2, 'Py_ssize_t', 'PyTuple_Size(args)')
        for sig in self.signatures:
            expect = len(sig) - 1
            println2('if (%(nargs)s == %(expect)d) {' % locals())
            method = StaticMethod(self.cls, sig[0], *sig[1:])
            method.name = self.name
            method.compile_body(indent_println(println2))
            println2('}')
        println2('PyErr_SetString(PyExc_TypeError, "Wrong # of args");')
        println2('return NULL;')
        println('}')

    @property
    def fullname(self):
        return '::'.join([self.cls.fullname, self.name])

    @property
    def mangled_name(self):
        return mangle(self.fullname)

class Constructor(StaticMethod):
    def compile_body(self, println):
        args = parse_arguments(println, 'args', *self.args)
        args = ', '.join(args)
        name = self.cls.fullname
        ctor = 'new %(name)s(%(args)s)' % locals()
        obj = declare(println, self.cls.pointer, ctor)
        ret = self.return_type.wrap(println, obj)
        return_value(println, ret)

class Destructor(Method):
    def compile_body(self, println):
        args = parse_arguments(println, 'args', *self.args)
        assert len(args) == 1
        dtor = 'delete %s;' % args[0]
        println(dtor)
        return_none(println)


class Namespace(object):
    def __init__(self, name):
        self.name = name

    def Class(self, *args, **kwargs):
        return Class(self.name, *args, **kwargs)

    def Function(self, *args, **kwargs):
        return Function(self.name, *args, **kwargs)

