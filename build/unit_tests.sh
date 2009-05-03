#!/usr/bin/env bash

#this is a bit of a hack, but it'll find the 'yeahbut' directory if
#it's somewhere under it 
while [[ ( $PWD != */yeahbut ) && ($PWD != /) ]] ; do
    cd ..;
done;

export PYTHONPATH="$PWD"

psql yb_test -U yb -f build_db.sql

cd frontend/

for test in test*.py
do
    echo "===== $test ====="
    python $test
done

cd ../backend/

for test in test*.py
do
    echo "===== $test ====="
    python $test
done
