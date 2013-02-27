from binding import *
from src.namespace import cl

cl.includes.add('llvm/Support/CommandLine.h')

ParseEnvironmentOptions = cl.Function('ParseEnvironmentOptions',
                                      Void,
                                      cast(str, ConstCharPtr), # progName
                                      cast(str, ConstCharPtr), # envvar
                                      cast(str, ConstCharPtr), # overiew = 0
                                      ).require_only(2)

