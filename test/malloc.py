from llvm.core import *

def test():
    m = Module.new('sdf')
    f = m.add_function(Type.function(Type.void(), []), 'foo')
    bb = f.append_basic_block('entry')
    b = Builder.new(bb)
    alloc = b.malloc(Type.int(), 'ha')
    inst = b.free(alloc)
    alloc = b.malloc_array(Type.int(), Constant.int(Type.int(), 10), 'hee')
    inst = b.free(alloc)
    b.ret_void()
    print(m)

if __name__ == '__main__':
    test()
