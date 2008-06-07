#!/usr/bin/env bash

# Quick/dirty build script for Yeah-But

# This one will include files not under source control. Success on
# this build does not imply success on a real build.

## Create build directory
#rm -rf build
#mkdir build

# Copy modified files to build location
cp -Rf ../backend/* build/
cp -Rf ../frontend/* build/
#cp -Rf ../../engine/trunk/* build/

# Start Yeah-But
cd build
python graypages.py
