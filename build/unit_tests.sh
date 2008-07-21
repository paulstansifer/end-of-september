## Clean build directory, but stash old contents (one generation only)
mkdir -p archive
mv -f build/* archive/

# Copy files to build location
cp -R ../backend/* build/
cp -R ../frontend/* build/
cp build_db.sql build/
#cp -Rf ../../engine/trunk/* build/


cd build
mysql -u yeahbut yb_test < build_db.sql
for test in test*.py
do
    echo "===== $test ====="
    python $test
done
