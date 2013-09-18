from binding import *
from src.namespace import sys

getDefaultTargetTriple = sys.Function('getDefaultTargetTriple',
                                      cast(ConstStdString, str))

if LLVM_VERSION >= (3, 3):
    getProcessTriple = sys.Function('getProcessTriple',
                                    cast(ConstStdString, str))

    isLittleEndianHost = sys.CustomFunction('isLittleEndianHost',
                                            'llvm_sys_isLittleEndianHost',
                                            cast(Bool, bool))

    isBigEndianHost = sys.CustomFunction('isBigEndianHost',
                                         'llvm_sys_isBigEndianHost',
                                         cast(Bool, bool))

else:

    isLittleEndianHost = sys.Function('isLittleEndianHost',
                                      cast(Bool, bool))

    isBigEndianHost = sys.Function('isBigEndianHost',
                                   cast(Bool, bool))


getHostCPUName = sys.Function('getHostCPUName',
                              cast(ConstStdString, str))

getHostCPUFeatures = sys.CustomFunction('getHostCPUFeatures',
                                        'llvm_sys_getHostCPUFeatures',
                                        PyObjectPtr, # bool: success?
                                        PyObjectPtr, # dict: store feature map
                                        )

