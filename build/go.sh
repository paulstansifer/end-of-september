#!/usr/bin/env bash

OLDWD=$PWD

#this is a bit of a hack, but it'll find the 'yeahbut' directory if
#it's somewhere under it 
while [[ ( $PWD != */yeahbut ) && ($PWD != /) ]] ; do
    cd ..;
done;

YB=$PWD
cd $OLDWD

if [ "$1" = "dbg" ]; then
    shift
    OPT="-m pdb"
fi


export PYTHONPATH="$YB"

# Start something
if [ "$1" = "tg" ]; then
    python $OPT $YB/frontend/terminalgray.py;
elif [ "$1" = "generate-state" ]; then
    python $OPT $YB/backend/state_filler.py;
elif [ "$1" = "ut" ]; then
    psql yb_test -U yb -q -f $YB/build/build_db.sql
    for test in $YB/frontend/test*.py
    do
        echo "===== $test ====="
        python $OPT $test
    done

    for test in $YB/backend/test*.py
    do
        echo "===== $test ====="
        python $OPT $test
    done
elif [ "$1" = "rebuild-just-db" ]; then
    psql yb -U yb -f $YB/build/build_db.sql
elif [ "$1" = "rebuild" ]; then
    psql yb -U yb -f $YB/build/build_db.sql
    python $OPT $YB/backend/state_filler.py
else
    cd $YB/frontend
    python $OPT $YB/frontend/graypages.py;
fi