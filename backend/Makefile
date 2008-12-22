OUT=../build/cpp
NEWMAT_LOC=../external/newmat11
LINK_FLAGS=-L$(NEWMAT_LOC) -L$(OUT)
INC_BASE=..



local_matrix_tools.o: local_matrix_tools.cpp
	mkdir -p $(OUT)
	make newmat
	g++ -Wall -O2 -c -o $(OUT)/$@ -g $? -I$(INC_BASE)

svd: svd.cpp
	mkdir -p $(OUT)
	make newmat
	make local_matrix_tools.o
	g++ -Wall -O2 -o $(OUT)/$@ -g $? -I$(INC_BASE) $(LINK_FLAGS) -lnewmat $(OUT)/local_matrix_tools.o

score: score.cpp
	mkdir -p $(OUT)
	make newmat
	make local_matrix_tools.o
	g++ -Wall -O2 -o $(OUT)/$@ -g $? -I$(INC_BASE) $(LINK_FLAGS) -lnewmat $(OUT)/local_matrix_tools.o

newmat:
	pwd
	cd $(NEWMAT_LOC); make -f nm_gnu.mak libnewmat.a
