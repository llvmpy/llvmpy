# ______________________________________________________________________

import llvm.core as lc

from llpython import bytetype

# ______________________________________________________________________

doslice = lc.Type.function(bytetype.li8_ptr, (
        bytetype.li8_ptr, bytetype.lc_size_t, bytetype.lc_size_t))

ipow = lc.Type.function(bytetype.li32, (bytetype.li32,
                                        bytetype.li32))

pymod = lc.Type.function(bytetype.li32, (bytetype.li32,
                                         bytetype.li32))

# ______________________________________________________________________
# End of llfunctys.py
