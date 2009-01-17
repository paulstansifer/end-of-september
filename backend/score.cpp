/* Inputs: cluster assignments (from clustering in R), raw vote data
 * Output: scores for articles, based on the number of votes they
 * received, and from which users.
 */


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


//As an optimization, it would be nice to have the vote data in
//transposed form, so we can process one article at a time, and
//therefore store a 1 by |users| blob of data at a time, instead of
//working with |users| by |articles|
void emit_scores(Matrix & cluster_assignments, Matrix & votes) {
  //count clusters
  int max_cluster = 0;
  for(int voter = 1; voter <= votes.ncols(); voter++) {
    max_cluster = max_cluster > cluster_assignments(voter, 1) ?
      max_cluster : (int)cluster_assignments(voter, 1); //always an integer
  }
  printf("Highest cluster: %d\n", max_cluster);

  //calculate cluster sizes
  int cluster_sizes[max_cluster];
  for(int i = 1; i <= max_cluster; i++) {
    cluster_sizes[i]=0;
  }
  for(int voter = 1; voter <= votes.ncols(); voter++) {
    cluster_sizes[(int)cluster_assignments(voter,1)]++;
  }

  for(int article = 1; article <= votes.nrows(); article++) {

    //zero out counter
    int clustered_votes[max_cluster];
    for(int i = 0; i < max_cluster; i++)
      clustered_votes[i] = 0;

    //count votes for this article, in bins by cluster
    for(int voter = 1; voter <= votes.ncols(); voter++) {
      if(votes(voter,article) > 0) {
        int voter_cluster = (int)cluster_assignments(voter,1);
        clustered_votes[voter_cluster]++;
      }
    }
    double total_value = 0;
    for(int i = 1; i <= max_cluster; i++) {
      total_value += 1.0 / pow(clustered_votes[i] / (double)cluster_sizes[i], 0.25);
    }
    printf("article %d has value %.2f\n", article, total_value);
  }
}

Matrix article_scores;

int main(int argc, char* argv[]) {
  Matrix cluster_assignments;
  Matrix votes;
  for(int i = 1; i < argc; i++) {
    if(strcmp(argv[i], "-c") == 0) {
      ifstream caf(argv[++i]);
      read_plain_matrix(cluster_assignments, caf);
    }
    if(strcmp(argv[i], "-v") == 0) {
      while(++i < argc) {
        ifstream vf(argv[i]);
        read_sparse_matrix(votes, vf);
      }
    }
  }
  emit_scores(cluster_assignments, votes);
}


