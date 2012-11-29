from llvm.core import *

class TBAABuilder(object):
    '''Simplify creation of TBAA metadata.
    
    Each TBAABuidler object operates on a module.  
    User can create multiple TBAABuilder on a module
    '''
    
    def __init__(self, module, rootid):
        '''
        module --- the module to use.
        root --- string name to identify the TBAA root.
        '''
        self.__module = module
        self.__rootid = rootid
        self.__rootmd = self.__new_md(rootid)

    @classmethod
    def new(cls, module, rootid):
        return cls(module, rootid)

    def get_node(self, name, parent=None, const=False):
        '''Returns a MetaData object representing a TBAA node.

        Use loadstore_instruction.set_metadata('tbaa', node) to 
        bind a type to a memory.
        '''
        parent = parent or self.root
        const = Constant.int(Type.int(), int(bool(const)))
        return self.__new_md(name, parent, const)

    @property
    def module(self):
        return self.__module

    @property
    def root(self):
        return self.__rootmd

    @property
    def root_name(self):
        return self.__rootid

    def __new_md(self, *args):
        contents = list(args)
        for i, v in enumerate(contents):
            if isinstance(v, str):
                contents[i] = MetaDataString.get(self.module, v)
        return MetaData.get(self.module, contents)

