#!/usr/bin/env python

from llvm.core import *
from cStringIO import StringIO


def make_module():
    test_module = """
    define i32 @sum(i32, i32) {
    entry:
            %2 = add i32 %0, %1
            ret i32 %2
    }
    """
    return Module.from_assembly(StringIO(test_module))


def test_align(m):
    f = m.get_function_named('sum')
    f.args[0].alignment = 16
    assert "align 16" in str(f)
    assert f.args[0].alignment == 16


m = make_module()
test_align(m)


