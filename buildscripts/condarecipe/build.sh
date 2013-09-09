#!/bin/bash

if [[ (`uname` == Linux) && (`uname -m` != armv6l) ]]
then
    export CC=gcc
	#gcc44
    export CXX=g++
	#g++44
fi

export LLVMPY_DYNLINK=$DISTRO_BUILD

$PYTHON setup.py install
