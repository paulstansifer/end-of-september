#!/usr/bin/env bash

# Quick/dirty build script for Yeah-But

# This one will include files not under source control. Success on
# this build does not imply success on a real build.

# Like fastest_build.sh but does an svn update first.

# Update to most recent build from source control
cd ../../
svn update
cd build/trunk

# Run build script
./fastest_build.sh
