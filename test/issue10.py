
from llvm.core import *
import llvm._core

m = Module.new('a')
ti = Type.int()
tf = Type.function(ti, [ti, ti])

f = m.add_function(tf, "func1")

bb = f.append_basic_block('entry')

b = Builder.new(bb)

# There are no instructions in bb. Positioning of the
# builder at beginning (or end) should succeed (trivially).

b.position_at_end(bb)
b.position_at_beginning(bb)

