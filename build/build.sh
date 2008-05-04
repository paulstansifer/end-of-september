#!/usr/bin/env bash

# Build script for Yeah-But

# Create build directory
rm -rf build
mkdir build

# Update to most recent build from source control
cd ../../
svn update
cd build/trunk
svn co https://svn2.hosted-projects.com/yeahbut/yeahbut/backend/trunk
cp -R trunk/* build/
rm -rf trunk
svn co https://svn2.hosted-projects.com/yeahbut/yeahbut/frontend/trunk
cp -R trunk/* build/
rm -rf trunk
svn co https://svn2.hosted-projects.com/yeahbut/yeahbut/engine/trunk
cp -R trunk/* build/
rm -rf trunk
cd build
python graypages.py
