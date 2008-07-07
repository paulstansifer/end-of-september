#!/bin/bash

# wed.sh
# yeahbutter
#
# Created by Paul Stansifer on 2008-01-02.

mkfifo inwards
mkfifo outwards

cat inwards | ../yeahbutter dl | tee user | $* | tee analyzer > outwards &
 
cat blank outwards > inwards