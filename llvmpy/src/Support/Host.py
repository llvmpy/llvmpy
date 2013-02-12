from binding import *
from src.namespace import sys

isLittleEndianHost = sys.Function('isLittleEndianHost',
                                  cast(Bool, bool))

isBigEndianHost = sys.Function('isBigEndianHost',
                               cast(Bool, bool))

getDefaultTargetTriple = sys.Function('getDefaultTargetTriple',
                                      cast(ConstStdString, str))

# llvm 3.3
#getProcessTriple = sys.Function('getProcessTriple',
#                                cast(ConstStdString, str))

getHostCPUName = sys.Function('getHostCPUName',
                              cast(ConstStdString, str))

getHostCPUFeatures = sys.CustomFunction('getHostCPUFeatures',
                                        'llvm_sys_getHostCPUFeatures',
                                        PyObjectPtr, # bool: success?
                                        PyObjectPtr, # dict: store feature map
                                        )

