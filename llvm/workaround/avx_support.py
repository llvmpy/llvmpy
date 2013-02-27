"""
Auto-detect avx and xsave

According to Intel manual [0], both AVX and XSAVE features must be present to
use AVX instructions.

References:

[0] Intel Architecture Instruction Set Extensions Programming Reference

http://software.intel.com/sites/default/files/m/a/b/3/4/d/41604-319433-012a.pdf

"""

import sys, os, subprocess

def detect_avx_support(option='detect'):
    '''Detect AVX support'''
    option = os.environ.get('LLVMPY_AVX_SUPPORT', option).lower()
    if option in ('disable', '0', 'false'):
        return False
    elif option in ('enable', '1', 'true'):
        return True
    else: # do detection
        plat = sys.platform
        if plat.startswith('darwin'):
            return detect_osx_like()
        elif plat.startswith('win32'):
            return False # don't know how to detect in windows
        else:
            return detect_unix_like()

def detect_unix_like():
    try:
        info = open('/proc/cpuinfo')
    except IOError:
        return False

    for line in info:
        if line.lstrip().startswith('flags'):
            features = line.split()
            if 'avx' in features and 'xsave' in features:
                # enable AVX if flags contain AVX
                return True
    return False

def detect_osx_like():
    try:
        info = subprocess.Popen(['sysctl', '-n', 'machdep.cpu.features'],
                                stdout=subprocess.PIPE)
    except OSError:
        return False

    features = info.stdout.read()
    features = features.split()
    return 'AVX1.0' in features and 'OSXSAVE' in features and 'XSAVE' in features


if __name__ == '__main__':
    print("AVX support: %s" % detect_avx_support())
