OUT=../build/cpp
NEWMAT_LOC=../external/newmat10
LINK_FLAGS=-L$(NEWMAT_LOC)
INC_BASE=..


offline: offline.cpp
	mkdir -p $(OUT)
	make newmat
	g++ -O2 -o $(OUT)/$@ -g $? -I$(INC_BASE) $(LINK_FLAGS) -lnewmat

newmat:
	pwd
	cd $(NEWMAT_LOC); make -f nm_gnu.mak libnewmat.a
