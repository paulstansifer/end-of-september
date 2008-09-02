#!/usr/bin/env bash

# Quick/dirty build script for Yeah-But

# This one will include files not under source control. Success on
# this build does not imply success on a real build.

## Clean build directory, but stash old contents (one generation only)
mkdir -p archive
mv -f build/* archive/

# Copy files to build location
cp -R ../backend/* build/
cp -R ../frontend/* build/
#cp -Rf ../../engine/trunk/* build/

# Start something
cd build
if (($1 == tg)); then
    python terminalgray.py;
else
    python graypages.py;
fi;
