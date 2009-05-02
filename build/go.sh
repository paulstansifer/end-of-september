#!/usr/bin/env bash

#this is a bit of a hack, but it'll find the 'yeahbut' directory if
#it's somewhere under it 
while [[ ( $PWD != */yeahbut ) && ($PWD != /) ]] ; do
    cd ..;
done;

export PYTHONPATH="$PWD"
cd frontend/

# Start something
if [ "$1" = "tg" ]; then
    python terminalgray.py;
elif [ "$1" = "sf" ]; then
    python ../backend/state_filler.py;
else
    python graypages.py;
fi;
