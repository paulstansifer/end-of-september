
#define WANT_STREAM
#define WANT_MATH

#include "external/newmat11/newmatap.h"
#include "external/newmat11/newmatio.h"

#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <math.h>

#include "local_matrix_tools.h"

using namespace std;

//TODO: pull out and generalize into read_plain_matrix
void read_plain(Matrix & m, char* filename) {
  ifstream matrixfile(filename, ifstream::in);
  char line[1024];
  matrixfile.getline(line, 1024);

  int spaces = 0;
  bool in_a_gap = true;
  for(char * i = line; *i != '\n'; i++) {
    if(*i == ' ') {
      if(!in_a_gap) {
        in_a_gap = true;
        spaces++;
      }
    } else {
      in_a_gap = false;
    }
  }
  int width = spaces + 1;

  int height = 1;
  while(!matrixfile.eof()) {
    matrixfile.getline(line,1024);
    if(strlen(line) > 1) { //non-empty lines
      height++;
    }
  }

  matrixfile.close();
  matrixfile.open(filename);
  m.ReSize(width, height);

  for(int x = 1; x <= width; x++) {
    for(int y = 1; y <= height; y++) {
      int val;
      matrixfile >> val;
      m(x,y) = val;
    }
  }
}

void emit_scores(Matrix & cluster_assignments, Matrix & votes) {
  int clusters = 
  for(int article = 0; article < votes.nrows(); article++) {
    for(int voter = 0; voter < votes.ncols(); voter++) {
      if(votes(voter,article) > 0) {
        int voter_cluster



}
  
int main(int argc, char* argv[]) {
  Matrix cluster_assignments;
  Matrix votes;
  for(int i = 1; i < argc; i++) {
    if(strcmp(argv[i], "-c") == 0) {
      //ifstream caf(argv[++i]);
      //read_sparse_matrix(cluster_assignments, caf);
      read_plain(cluster_assignments, argv[++i]);
    }
    if(strcmp(argv[i], "-v") == 0) {
      while(++i < argc) {
        ifstream vf(argv[i]);
        read_sparse_matrix(votes, vf);
      }
    }
  }
  
  
}
