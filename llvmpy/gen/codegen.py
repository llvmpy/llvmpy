import re, contextlib

NULL = 'NULL'

_symbols = set()

def wrap_println_from_file(file):
    def println(s=''):
        file.write(s)
        file.write('\n')
    return println

def indent(println):
    def _println(s=''):
        println("%s%s" % (' '* 4, s))
    return _println

def quote(txt):
    return '"%s"' % txt

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

_re_mangle_pattern = re.compile(r'[ _<>\*&,]')

def mangle(name):
    def repl(m):
        s = m.group(0)
        if s in '<>*&':
            return ''
        elif s in ' ,':
            return '_'
        elif s in '_':
            return '__'
        else:
            assert False
    name = _re_mangle_pattern.sub(repl, name)
    return name.replace('::', '_')

def pycapsule_new(println, ptr, name, clsname):
    # build capsule
    name_soften = mangle(name)
    var = new_symbol('pycap_%s' % name_soften)
    fmt = 'PyObject* %(var)s = pycapsule_new(%(ptr)s, "%(name)s", "%(clsname)s");'
    println(fmt % locals())
    println('if (!%(var)s) return NULL;' % locals())
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


class CodeWriterBase(object):
    def __init__(self, println):
        self.println = println
        self.used_symbols = set()

    @contextlib.contextmanager
    def indent(self):
        old = self.println
        self.println = indent(self.println)
        yield
        self.println = old

    @contextlib.contextmanager
    def py_function(self, name):
        self.println('static')
        self.println('PyObject*')
        with self.block('%(name)s(PyObject* self, PyObject* args)' % locals()):
            self.used_symbols.add('self')
            self.used_symbols.add('args')
            yield
        self.println()

    def new_symbol(self, name):
        if name in self.used_symbols:
            ct = 1
            orig = name
            while name in self.used_symbols:
                name = '%s%d' % (orig, ct)
                ct += 1
        self.used_symbols.add(name)
        return name

class CppCodeWriter(CodeWriterBase):
    @contextlib.contextmanager
    def block(self, lead):
        self.println(lead)
        self.println('{')
        with self.indent():
            yield
        self.println('}')

    def declare(self, typ, init=None):
        typ_soften = mangle(typ)
        var = self.new_symbol('var_%s' % typ_soften)
        if init is None:
            self.println('%(typ)s %(var)s;' % locals())
        else:
            self.println('%(typ)s %(var)s = %(init)s;' % locals())
        return var

    def return_value(self, val):
        if val is None:
            self.println('Py_RETURN_NONE;')
        else:
            self.println('return %s;' % val)

    def return_null(self):
        self.return_value(NULL)

    def parse_arguments(self, var, *args):
        typecodes = []
        holders = []
        argvals = []
        for arg in args:
            typecodes.append(arg.format)
            val = self.declare('PyObject*')
            argvals.append(val)
            holders.append('&' + val)

        items = [var, '"%s"' % (''.join(typecodes))] + holders
        with self.block('if(!PyArg_ParseTuple(%s))' % ', '.join(items)):
            self.return_null()

        # unwrap
        unwrapped = []
        for arg, val in zip(args, argvals):
            unwrapped.append(arg.unwrap(self, val))

        return unwrapped

    def call(self, func, retty, *args):
        arglist = ', '.join(args)
        stmt = '%(func)s(%(arglist)s)' % locals()
        if retty == 'void':
            self.println(stmt + ';')
        else:
            return self.declare(retty, stmt)

    def method_call(self, func, retty, *args):
        this = args[0]
        arglist = ', '.join(args[1:])
        if func == 'delete':
            assert not arglist
            stmt = 'delete %(this)s' % locals()
        elif func == 'new':
            alloctype = retty.rstrip(' *')
            stmt = 'new %(alloctype)s(%(arglist)s)' % locals()
        else:
            stmt = '%(this)s->%(func)s(%(arglist)s)' % locals()
        if retty == 'void':
            self.println('%s;' % stmt)
        else:
            return self.declare(retty, stmt)

    def pycapsule_new(self, ptr, name, clsname):
        name_soften = mangle(name)
        cast_to_base = 'cast_to_base<%s >::from(%s)' % (name, ptr)
        ret = self.call('pycapsule_new', 'PyObject*', cast_to_base, quote(name),
                        quote(clsname))
        with self.block('if (!%(ret)s)' % locals()):
            self.return_null()
        return ret

    def die_if_false(self, val, verbose=None):
        with self.block('if(!%(val)s)' % locals()):
            if verbose:
                self.println('puts("Error: %s");' % verbose)
            self.return_null()

    def raises(self, exccls, msg):
        exc = 'PyExc_%s' % exccls.__name__
        self.println('PyErr_SetString(%s, "%s");' % (exc, msg))
        self.return_null()


class PyCodeWriter(CodeWriterBase):
    @contextlib.contextmanager
    def block(self, lead):
        self.println(lead)
        with self.indent():
            yield

    @contextlib.contextmanager
    def function(self, func, args=(), varargs=None):
        with self.scope():
            arguments = []
            for arg in args:
                arguments.append(self.new_symbol(arg))
            if varargs:
                varargs = self.new_symbol(varargs)
                arguments.append('*%s' % varargs)
            arglist = ', '.join(arguments)
            with self.block('def %(func)s(%(arglist)s):' % locals()):
                if arguments:
                    arguments[-1] = arguments[-1].lstrip('*')
                    if len(arguments) > 1:
                        yield arguments
                    else:
                        yield arguments[0]
                else:
                    yield

    @contextlib.contextmanager
    def scope(self):
        self.old = self.used_symbols
        self.used_symbols = set()
        yield
        self.used_symbols = self.old

    def release_ownership(self, val):
        self.println('capsule.release_ownership(%(val)s)' % locals())

    def unwrap_many(self, args):
        unwrapped = self.new_symbol('unwrapped')
        self.println('%(unwrapped)s = list(map(capsule.unwrap, %(args)s))' % locals())
        return unwrapped

    def unwrap(self, val):
        return self.call('capsule.unwrap', args=(val,), ret='unwrapped')

    def wrap(self, val, owned):
        wrapped = self.new_symbol('wrapped')
        self.println('%(wrapped)s = capsule.wrap(%(val)s, %(owned)s)' % locals())
        return wrapped

    def call(self, func, args=(), varargs=None, ret='ret'):
        arguments = []
        for arg in args:
            arguments.append(arg)
        if varargs:
            arguments.append('*%s' % varargs)
        arglist = ', '.join(arguments)
        ret = self.new_symbol(ret)
        self.println('%(ret)s = %(func)s(%(arglist)s)' % locals())
        return ret

    def return_value(self, val=None):
        if val is None:
            val = ''
        self.println('return %s' % val)


