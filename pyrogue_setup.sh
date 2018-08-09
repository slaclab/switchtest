#!/usr/bin/env bash

#source /afs/slac/g/lcls/package/pyrogue/rogue/v2.10.0/setup_slac.sh
#source /afs/slac/g/lcls/package/pyrogue/rogue/v2.10.0/setup_rogue.sh

source /afs/slac/g/lcls/package/pyrogue/rogue/ESROGUE-266/setup_slac.sh
source /afs/slac/g/lcls/package/pyrogue/rogue/ESROGUE-266/setup_rogue.sh

export PYTHONPATH=${PWD}/switchTest.python/python/:$PYTHONPATH
