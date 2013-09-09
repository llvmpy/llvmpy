import inspect, textwrap
import functools
import codegen as cg
import os

_rank = 0
namespaces = {}

RESERVED = frozenset(['None'])

def makedir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

class SubModule(object):
    def __init__(self):
        self.methods = []
        self.enums = []
        self.classes = []
        self.namespaces = []
        self.attrs = []
        self.includes = set()

    def aggregate_includes(self):
        includes = set(self.includes)
        for unit in self.iter_all():
            if isinstance(unit, SubModule):
                includes |= unit.aggregate_includes()
            else:
                includes |= unit.includes
        return includes

    def aggregate_downcast(self):
        dclist = []
        for cls in self.classes:
            for bcls in cls.downcastables:
                from_to = bcls.fullname, cls.fullname
                name = 'downcast_%s_to_%s' % tuple(map(cg.mangle, from_to))
                fn = Function(namespaces[''], name, ptr(cls), ptr(bcls))
                dclist.append((from_to, fn))
        for ns in self.namespaces:
            dclist.extend(ns.aggregate_downcast())
        return dclist

    def iter_all(self):
        for fn in self.methods:
            yield fn
        for cls in self.classes:
            yield cls
        for enum in self.enums:
            yield enum
        for attr in self.attrs:
            yield attr
        for ns in self.namespaces:
            yield ns


    def generate_method_table(self, println):
        writer = cg.CppCodeWriter(println)
        writer.println('static')
        writer.println('PyMethodDef meth_%s[] = {' % cg.mangle(self.fullname))
        with writer.indent():
            fmt = '{ "%(name)s", (PyCFunction)%(func)s, METH_VARARGS, NULL },'
            for meth in self.methods:
                name = meth.name
                func = meth.c_name
                writer.println(fmt % locals())
            for enumkind in self.enums:
                for enum in enumkind.value_names:
                    name = enum
                    func = enumkind.c_name(enum)
                    writer.println(fmt % locals())
            for attr in self.attrs:
                # getter
                name = attr.getter_name
                func = attr.getter_c_name
                writer.println(fmt % locals())
                # setter
                name = attr.setter_name
                func = attr.setter_c_name
                writer.println(fmt % locals())
            writer.println('{ NULL },')
        writer.println('};')
        writer.println()

#    def generate_downcasts(self, println):
#        for ((fromty, toty), fn) in self.downcastlist:
#            name = fn.name
#            fmt = '''
#static
#%(toty)s* %(name)s(%(fromty)s* arg)
#{
#    return typecast< %(toty)s >::from(arg);
#}
#                '''
#            println(fmt % locals())
#
#            fn.generate_cpp(println)

    def generate_cpp(self, println, extras=()):
        for unit in self.iter_all():
            unit.generate_cpp(println)
        self.generate_method_table(println)
        self.generate_submodule_table(println, extras=extras)

    def generate_submodule_table(self, println, extras=()):
        writer = cg.CppCodeWriter(println)
        writer.println('static')
        name = cg.mangle(self.fullname)
        writer.println('SubModuleEntry submodule_%(name)s[] = {' % locals())
        with writer.indent():
            for cls in self.classes:
                name = cls.name
                table = cg.mangle(cls.fullname)
                writer.println('{ "%(name)s", meth_%(table)s, NULL },' %
                               locals())
            for ns in self.namespaces:
                name = ns.localname
                table = cg.mangle(ns.fullname)
                fmt = '{ "%(name)s", meth_%(table)s, submodule_%(table)s },'
                writer.println(fmt % locals())
            for name, table in extras:
                writer.println('{ "%(name)s", %(table)s, NULL },' % locals())
            writer.println('{ NULL }')
        writer.println('};')
        writer.println('')

    def generate_py(self, rootdir='.', name=''):
        name = name or self.localname
        if self.namespaces: # should make new directory
            path = os.path.join(rootdir, name)
            makedir(path)
            filepath = os.path.join(path, '__init__.py')
        else:
            filepath = os.path.join(rootdir, '%s.py' % name)
        with open(filepath, 'w') as pyfile:
            println = cg.wrap_println_from_file(pyfile)
            println('from llvmpy import _api, capsule')
            for ns in self.namespaces:
                println('from . import %s' % ns.localname)
            println()
            for unit in self.iter_all():
                if not isinstance(unit, Namespace):
                    writer = cg.PyCodeWriter(println)
                    unit.compile_py(writer)

        for ns in self.namespaces:
            ns.generate_py(rootdir=path)


class Namespace(SubModule):
    def __init__(self, name):
        SubModule.__init__(self)
        self.name = name = name.lstrip(':')
        namespaces[name] = self

    def Class(self, *bases):
        cls = Class(self, *bases)
        self.classes.append(cls)
        return cls

    def Function(self, *args):
        fn = Function(self, *args)
        self.methods.append(fn)
        return fn

    def CustomFunction(self, *args):
        fn = CustomFunction(self, *args)
        self.methods.append(fn)
        return fn

    def Enum(self, name, *value_names):
        enum = Enum(*value_names)
        enum.parent = self
        enum.name = name
        self.enums.append(enum)
        assert name not in vars(self), 'Duplicated'
        setattr(self, name, enum)
        return enum

    def Namespace(self, name):
        ns = Namespace('::'.join([self.name, name]))
        self.namespaces.append(ns)
        return ns

    @property
    def fullname(self):
        return self.name

    @property
    def py_name(self):
        return self.name.replace('::', '.')

    @property
    def localname(self):
        return self.name.rsplit('::', 1)[-1]

    def __str__(self):
        return self.name

class _Type(object):
    pass

class BuiltinTypes(_Type):
    def __init__(self, name):
        self.name = name

    @property
    def fullname(self):
        return self.name

    def wrap(self, writer, var):
        return var

    def unwrap(self, writer, var):
        return var

Void = BuiltinTypes('void')
Unsigned = BuiltinTypes('unsigned')
UnsignedLongLong = BuiltinTypes('unsigned long long') # used in llvm-3.2
LongLong = BuiltinTypes('long long')
Float = BuiltinTypes('float')
Double = BuiltinTypes('double')
Uint64 = BuiltinTypes('uint64_t')
Int64 = BuiltinTypes('int64_t')
Int = BuiltinTypes('int')
Size_t = BuiltinTypes('size_t')
VoidPtr = BuiltinTypes('void*')
Bool = BuiltinTypes('bool')
StdString = BuiltinTypes('std::string')
ConstStdString = BuiltinTypes('const std::string')
ConstCharPtr = BuiltinTypes('const char*')
PyObjectPtr = BuiltinTypes('PyObject*')
PyObjectPtr.format='O'

class Class(SubModule, _Type):
    format = 'O'

    def __init__(self, ns, *bases):
        SubModule.__init__(self)
        self.ns = ns
        self.bases = bases
        self._is_defined = False
        self.pymethods = []
        self.downcastables = set()

    def __call__(self, defn):
        assert not self._is_defined
        # process the definition in "defn"
        self.name = getattr(defn, '_name_', defn.__name__)

        for k, v in defn.__dict__.items():
            if isinstance(v, Method):
                self.methods.append(v)
                if isinstance(v, Constructor):
                    for sig in v.signatures:
                        sig[0] = ptr(self)
                v.name = k
                v.parent = self
            elif isinstance(v, Enum):
                self.enums.append(v)
                v.name = k
                v.parent = self
                assert k not in vars(self), "Duplicated: %s" % k
                setattr(self, k, v)
            elif isinstance(v, Attr):
                self.attrs.append(v)
                v.name = k
                v.parent = self
            elif isinstance(v, CustomPythonMethod):
                self.pymethods.append(v)
            elif k == '_include_':
                if isinstance(v, str):
                    self.includes.add(v)
                else:
                    for i in v:
                        self.includes.add(i)
            elif k == '_realname_':
                self.realname = v
            elif k == '_downcast_':
                if isinstance(v, Class):
                    self.downcastables.add(v)
                else:
                    for i in v:
                        self.downcastables.add(i)
        return self

    def compile_py(self, writer):
        clsname = self.name
        bases = 'capsule.Wrapper'
        if self.bases:
            bases = ', '.join(x.name for x in self.bases)
        writer.println('@capsule.register_class("%s")' % self.fullname)
        with writer.block('class %(clsname)s(%(bases)s):' % locals()):
            writer.println('_llvm_type_ = "%s"' % self.fullname)
            for enum in self.enums:
                enum.compile_py(writer)
            for meth in self.methods:
                meth.compile_py(writer)
            for meth in self.pymethods:
                meth.compile_py(writer)
            for attr in self.attrs:
                attr.compile_py(writer)
        writer.println()

    @property
    def capsule_name(self):
        if self.bases:
            return self.bases[-1].capsule_name
        else:
            return self.fullname

    @property
    def fullname(self):
        try:
            name = self.realname
        except AttributeError:
            name = self.name
        return '::'.join([self.ns.fullname, name])

    @property
    def py_name(self):
        ns = self.ns.name.split('::')
        return '.'.join(ns + [self.name])

    def __str__(self):
        return self.fullname

    def unwrap(self, writer, val):
        fmt = 'PyCapsule_GetPointer(%(val)s, "%(name)s")'
        name = self.capsule_name
        raw = writer.declare('void*', fmt % locals())
        writer.die_if_false(raw, verbose=name)
        ptrty = ptr(self).fullname
        ty = self.fullname
        fmt = 'unwrap_as<%(ty)s, %(name)s >::from(%(raw)s)'
        casted = writer.declare(ptrty, fmt % locals())
        writer.die_if_false(casted)
        return casted

    def wrap(self, writer, val):
        copy = 'new %s(%s)' % (self.fullname, val)
        return writer.pycapsule_new(copy, self.capsule_name, self.fullname)


class Enum(object):
    format = 'O'

    def __init__(self, *value_names):
        self.parent = None
        if len(value_names) == 1:
            value_names = list(filter(bool, value_names[0].replace(',', ' ').split()))
        self.value_names = value_names
        self.includes = set()

    @property
    def fullname(self):
        try:
            name = self.realname
        except AttributeError:
            name = self.name
        return '::'.join([self.parent.fullname, name])

    def __str__(self):
        return self.fullname

    def wrap(self, writer, val):
        ret = writer.declare('PyObject*', 'PyInt_FromLong(%s)' % val)
        return ret

    def unwrap(self, writer, val):
        convert_long_to_enum = '(%s)PyInt_AsLong(%s)' % (self.fullname, val)
        ret = writer.declare(self.fullname, convert_long_to_enum)
        return ret

    def c_name(self, enum):
        return cg.mangle("%s_%s_%s" % (self.parent, self.name, enum))

    def generate_cpp(self, println):
        self.compile_cpp(cg.CppCodeWriter(println))

    def compile_cpp(self, writer):
        for enum in self.value_names:
            with writer.py_function(self.c_name(enum)):
                ret = self.wrap(writer, '::'.join([self.parent.fullname, enum]))
                writer.return_value(ret)

    def compile_py(self, writer):
        with writer.block('class %s:' % self.name):
            writer.println('_llvm_type_ = "%s"' % self.fullname)
            for v in self.value_names:
                if v in RESERVED:
                    k = '%s_' % v
                    fmt = '%(k)s = getattr(%(p)s, "%(v)s")()'
                else:
                    k = v
                    fmt = '%(k)s = %(p)s.%(v)s()'
                p = '.'.join(['_api'] + self.parent.fullname.split('::'))
                writer.println(fmt % locals())
        writer.println()

class Method(object):
    _kind_ = 'meth'

    def __init__(self, return_type=Void, *args):
        self.parent = None
        self.signatures = []
        self.includes = set()
        self._add_signature(return_type, *args)
        self.disowning = False

    def _add_signature(self, return_type, *args):
        prev_lens = set(map(len, self.signatures))
        cur_len = len(args) + 1
        if cur_len in prev_lens:
            raise Exception('Only support overloading with different number'
                            ' of arguments')
        self.signatures.append([return_type] + list(args))

    def __ior__(self, method):
        assert type(self) is type(method)
        for sig in method.signatures:
            self._add_signature(sig[0], *sig[1:])
        return self

    @property
    def fullname(self):
        return '::'.join([self.parent.fullname, self.realname]).lstrip(':')

    @property
    def realname(self):
        try:
            return self.__realname
        except AttributeError:
            return self.name

    @realname.setter
    def realname(self, v):
        self.__realname = v

    @property
    def c_name(self):
        return cg.mangle("%s_%s" % (self.parent, self.name))

    def __str__(self):
        return self.fullname

    def generate_cpp(self, println):
        self.compile_cpp(cg.CppCodeWriter(println))

    def compile_cpp(self, writer):
        with writer.py_function(self.c_name):
            if len(self.signatures) == 1:
                sig = self.signatures[0]
                retty = sig[0]
                argtys = sig[1:]
                self.compile_cpp_body(writer, retty, argtys)
            else:
                nargs = writer.declare('Py_ssize_t', 'PyTuple_Size(args)')
                for sig in self.signatures:
                    retty = sig[0]
                    argtys = sig[1:]
                    expect = len(argtys)
                    if (not isinstance(self, StaticMethod) and
                        isinstance(self.parent, Class)):
                        # Is a instance method, add 1 for "this".
                        expect += 1
                    with writer.block('if (%(expect)d == %(nargs)s)' % locals()):
                        self.compile_cpp_body(writer, retty, argtys)
                writer.raises(TypeError, 'Invalid number of args')

    def compile_cpp_body(self, writer, retty, argtys):
        args = writer.parse_arguments('args', ptr(self.parent), *argtys)
        ret = writer.method_call(self.realname, retty.fullname, *args)
        writer.return_value(retty.wrap(writer, ret))

    def compile_py(self, writer):
        decl = writer.function(self.name, args=('self',), varargs='args')
        with decl as (this, varargs):
            unwrap_this = writer.unwrap(this)
            if self.disowning:
                writer.release_ownership(unwrap_this)
            unwrapped = writer.unwrap_many(varargs)
            self.process_ownedptr_args(writer, unwrapped)
            func = '.'.join([self.parent.py_name, self.name])
            ret = writer.call('_api.%s' % func,
                              args=(unwrap_this,), varargs=unwrapped)

            wrapped = writer.wrap(ret, self.is_return_ownedptr())

            writer.return_value(wrapped)
            writer.println()

    def require_only(self, num):
        '''Require only "num" of argument.
        '''
        assert len(self.signatures) == 1
        sig = self.signatures[0]
        ret = sig[0]
        args = sig[1:]
        arg_ct = len(args)

        for i in range(num, arg_ct):
            self._add_signature(ret, *args[:i])

        return self

    def is_return_ownedptr(self):
        retty = self.signatures[0][0]
        return isinstance(retty, ownedptr)

    def process_ownedptr_args(self, writer, unwrapped):
        argtys = self.signatures[0][1:]
        for i, ty in enumerate(argtys):
            if isinstance(ty, ownedptr):
                with writer.block('if len(%s) > %d:' % (unwrapped, i)):
                    writer.release_ownership('%s[%d]' % (unwrapped, i))

class CustomMethod(Method):
    def __init__(self, methodname, retty, *argtys):
        super(CustomMethod, self).__init__(retty, *argtys)
        self.methodname = methodname

    def compile_cpp_body(self, writer, retty, argtys):
        args = writer.parse_arguments('args', ptr(self.parent), *argtys)
        ret = writer.call(self.methodname, retty.fullname, *args)
        writer.return_value(retty.wrap(writer, ret))


class StaticMethod(Method):

    def compile_cpp_body(self, writer, retty, argtys):
        assert isinstance(self.parent, Class)
        args = writer.parse_arguments('args', *argtys)
        ret = self.compile_cpp_call(writer, retty, args)
        writer.return_value(retty.wrap(writer, ret))

    def compile_cpp_call(self, writer, retty, args):
        ret = writer.call(self.fullname, retty.fullname, *args)
        return ret

    def compile_py(self, writer):
        writer.println('@staticmethod')
        decl = writer.function(self.name, varargs='args')
        with decl as varargs:
            unwrapped = writer.unwrap_many(varargs)
            self.process_ownedptr_args(writer, unwrapped)

            func = '.'.join([self.parent.py_name, self.name])
            ret = writer.call('_api.%s' % func, varargs=unwrapped)
            wrapped = writer.wrap(ret, self.is_return_ownedptr())
            writer.return_value(wrapped)
            writer.println()

class CustomStaticMethod(StaticMethod):
    def __init__(self, methodname, retty, *argtys):
        super(CustomStaticMethod, self).__init__(retty, *argtys)
        self.methodname = methodname

    def compile_cpp_body(self, writer, retty, argtys):
        args = writer.parse_arguments('args', *argtys)
        ret = writer.call(self.methodname, retty.fullname, *args)
        writer.return_value(retty.wrap(writer, ret))

class Function(Method):
    _kind_ = 'func'

    def __init__(self, parent, name, return_type=Void, *args):
        super(Function, self).__init__(return_type, *args)
        self.parent = parent
        self.name = name

    def compile_cpp_body(self, writer, retty, argtys):
        args = writer.parse_arguments('args', *argtys)
        ret = writer.call(self.fullname, retty.fullname, *args)
        writer.return_value(retty.wrap(writer, ret))

    def compile_py(self, writer):
        with writer.function(self.name, varargs='args') as varargs:
            unwrapped = writer.unwrap_many(varargs)
            self.process_ownedptr_args(writer, unwrapped)
            func = '.'.join([self.parent.py_name, self.name]).lstrip('.')
            ret = writer.call('_api.%s' % func, varargs=unwrapped)
            wrapped = writer.wrap(ret, self.is_return_ownedptr())
            writer.return_value(wrapped)
        writer.println()

class CustomFunction(Function):
    def __init__(self, parent, name, realname, return_type=Void, *args):
        super(CustomFunction, self).__init__(parent, name, return_type, *args)
        self.realname = realname

    @property
    def fullname(self):
        return self.realname

class Destructor(Method):
    _kind_ = 'dtor'

    def __init__(self):
        super(Destructor, self).__init__()

    def compile_cpp_body(self, writer, retty, argtys):
        assert isinstance(self.parent, Class)
        assert not argtys
        args = writer.parse_arguments('args', ptr(self.parent), *argtys)
        writer.println('delete %s;' % args[0])
        writer.return_value(None)

    def compile_py(self, writer):
        func = '.'.join([self.parent.py_name, self.name])
        writer.println('_delete_ = _api.%s' % func)


class Constructor(StaticMethod):
    _kind_ = 'ctor'

    def __init__(self, *args):
        super(Constructor, self).__init__(Void, *args)

    def compile_cpp_call(self, writer, retty, args):
        alloctype = retty.fullname.rstrip(' *')
        arglist = ', '.join(args)
        stmt = 'new %(alloctype)s(%(arglist)s)' % locals()
        ret = writer.declare(retty.fullname, stmt)
        return ret

class ref(_Type):
    def __init__(self, element):
        assert isinstance(element, Class), type(element)
        self.element = element
        self.const = False

    def __str__(self):
        return self.fullname

    @property
    def fullname(self):
        if self.const:
            return 'const %s&' % self.element.fullname
        else:
            return '%s&' % self.element.fullname

    @property
    def capsule_name(self):
        return self.element.capsule_name

    @property
    def format(self):
        return self.element.format

    def wrap(self, writer, val):
        p = writer.declare(const(ptr(self.element)).fullname, '&%s' % val)
        return writer.pycapsule_new(p, self.capsule_name, self.element.fullname)

    def unwrap(self, writer, val):
        p = self.element.unwrap(writer, val)
        return writer.declare(self.fullname, '*%s' % p)


class ptr(_Type):
    def __init__(self, element):
        assert isinstance(element, Class)
        self.element = element
        self.const = False

    @property
    def fullname(self):
        if self.const:
            return 'const %s*' % self.element
        else:
            return '%s*' % self.element

    @property
    def format(self):
        return self.element.format

    def unwrap(self, writer, val):
        ret = writer.declare(self.fullname, 'NULL')
        with writer.block('if (%(val)s != Py_None)' % locals()):
            val = self.element.unwrap(writer, val)
            writer.println('%(ret)s = %(val)s;' % locals())
        return ret

    def wrap(self, writer, val):
        return writer.pycapsule_new(val, self.element.capsule_name,
                                    self.element.fullname)

class ownedptr(ptr):
    pass

def const(ptr_or_ref):
    ptr_or_ref.const = True
    return ptr_or_ref

class cast(_Type):
    format = 'O'

    def __init__(self, original, target):
        self.original = original
        self.target = target

    @property
    def fullname(self):
        return self.binding_type.fullname

    @property
    def python_type(self):
        if not isinstance(self.target, _Type):
            return self.target
        else:
            return self.original

    @property
    def binding_type(self):
        if isinstance(self.target, _Type):
            return self.target
        else:
            return self.original

    def wrap(self, writer, val):
        dst = self.python_type.__name__
        if dst == 'int':
            unsigned = set([Unsigned, UnsignedLongLong, Uint64,
                            Size_t, VoidPtr])
            signed = set([LongLong, Int64, Int])
            assert self.binding_type in unsigned|signed
            if self.binding_type in signed:
                signflag = 'signed'
            else:
                signflag = 'unsigned'
            fn = 'py_%(dst)s_from_%(signflag)s' % locals()
        else:
            fn = 'py_%(dst)s_from' % locals()
        return writer.call(fn, 'PyObject*', val)

    def unwrap(self, writer, val):
        src = self.python_type.__name__
        dst = self.binding_type.fullname
        ret = writer.declare(dst)
        fn = 'py_%(src)s_to' % locals()
        status = writer.call(fn, 'int', val, ret)
        writer.die_if_false(status)
        return ret


class CustomPythonMethod(object):
    def __init__(self, fn):
        src = inspect.getsource(fn)
        lines = textwrap.dedent(src).splitlines()
        for i, line in enumerate(lines):
            if not line.startswith('@'):
                break
        self.sourcelines = lines[i:]

    def compile_py(self, writer):
        for line in self.sourcelines:
            writer.println(line)

class CustomPythonStaticMethod(CustomPythonMethod):
    def compile_py(self, writer):
        writer.println('@staticmethod')
        super(CustomPythonStaticMethod, self).compile_py(writer)


class Attr(object):
    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter
        self.includes = set()

    @property
    def fullname(self):
        try:
            name = self.realname
        except AttributeError:
            name = self.name
        return '::'.join([self.parent.fullname, name])

    def __str__(self):
        return self.fullname

    @property
    def getter_name(self):
        return '%s_get' % self.name

    @property
    def setter_name(self):
        return '%s_set' % self.name

    @property
    def getter_c_name(self):
        return cg.mangle('%s_get' % self.fullname)

    @property
    def setter_c_name(self):
        return cg.mangle('%s_set' % self.fullname)

    def generate_cpp(self, println):
        self.compile_cpp(cg.CppCodeWriter(println))

    def compile_cpp(self, writer):
        # getter
        with writer.py_function(self.getter_c_name):
            (this,) = writer.parse_arguments('args', ptr(self.parent))
            attr = self.name
            ret = writer.declare(self.getter.fullname,
                                 '%(this)s->%(attr)s' % locals())
            writer.return_value(self.getter.wrap(writer, ret))
        # setter
        with writer.py_function(self.setter_c_name):
            (this, value) = writer.parse_arguments('args', ptr(self.parent),
                                                   self.setter)
            attr = self.name
            writer.println('%(this)s->%(attr)s = %(value)s;' % locals())
            writer.return_value(None)

    def compile_py(self, writer):
        name = self.name
        parent = '.'.join(self.parent.fullname.split('::'))
        getter = '.'.join([parent, self.getter_name])
        setter = '.'.join([parent, self.setter_name])
        writer.println('@property')
        with writer.block('def %(name)s(self):' % locals()):
            unself = writer.unwrap('self')
            ret = writer.new_symbol('ret')
            writer.println('%(ret)s = _api.%(getter)s(%(unself)s)' % locals())
            is_ownedptr = isinstance(self.getter, ownedptr)
            writer.return_value(writer.wrap(ret, is_ownedptr))
        writer.println()
        writer.println('@%(name)s.setter' % locals())
        with writer.block('def %(name)s(self, value):' % locals()):
            unself = writer.unwrap('self')
            unvalue = writer.unwrap('value')
            if isinstance(self.setter, ownedptr):
                writer.release_ownership(unvalue)
            writer.println('return _api.%(setter)s(%(unself)s, %(unvalue)s)' %
                           locals())
        writer.println()


#
# Pick-up environ var
#

TARGETS_BUILT = os.environ.get('LLVM_TARGETS_BUILT', '').split()

def _parse_llvm_version(ver):
    import re
    m = re.compile(r'(\d+)\.(\d+)').match(ver)
    assert m
    major, minor = m.groups()
    return int(major), int(minor)

LLVM_VERSION = _parse_llvm_version(os.environ['LLVMPY_LLVM_VERSION'])

