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


double popularity_reduction = 0.65;

//As an optimization, it would be nice to have the vote data in
//transposed form, so we can process one article at a time, and
//therefore store a 1 by |users| blob of data at a time, instead of
//working with |users| by |articles|
void emit_scores(Matrix & cluster_assignments, Matrix & votes) {

  double top_score = 0;
  int best_article = 0;

  int top_raw = 0;
  int rawest_article = 0;

  //count clusters
  int max_cluster = 0;
  for(int voter = 1; voter <= votes.nrows(); voter++) {
    max_cluster = max_cluster > cluster_assignments(voter, 1) ?
      max_cluster : (int)cluster_assignments(voter, 1); //always an integer
  }
  printf("#Highest cluster: %d\n", max_cluster);

  //calculate cluster sizes
  int cluster_sizes[max_cluster];
  for(int i = 1; i <= max_cluster; i++) {
    cluster_sizes[i]=0;
  }
  for(int voter = 1; voter <= votes.nrows(); voter++) {
    cluster_sizes[(int)cluster_assignments(voter,1)]++;
  }
  for(int i = 1; i <= max_cluster; i++) {
    printf("#cluster %d has size %d.\n", i, cluster_sizes[i]);
  }


  for(int article = 1; article <= votes.ncols(); article++) {
    double cscores[max_cluster+1]; //debugging

    //zero out counter
    int clustered_votes[max_cluster+1];
    for(int i = 0; i <= max_cluster; i++)
      clustered_votes[i] = 0;

    //double total_proportional_votes = 0.0;
    int effective_clusters = 0;

    int raw_score = 0;
    //count votes for this article, in bins by cluster
    for(int voter = 1; voter <= votes.nrows(); voter++) {
      if(votes(voter,article) > 0) {
        int voter_cluster = (int)cluster_assignments(voter,1);
        clustered_votes[voter_cluster]++;
        raw_score++;
      }
    }
    double total_value = 0;
    for(int i = 1; i <= max_cluster; i++) {
      if(cluster_sizes[i] < 5) continue; //too extreme (HACK)
      effective_clusters++;
      cscores[i] = clustered_votes[i] / pow((double)cluster_sizes[i], 0.75);
      //total_proportional_votes += clustered_votes[i] / cluster_sizes[i];

      total_value += clustered_votes[i] / pow((double)cluster_sizes[i], 0.75);
    }

    /*
    const double ave_proportional_votes = total_proportional_votes / effective_clusters;

    
    int total_overreach = 0;
    for(int i = 1; i <= max_cluster; i++) {
      if(cluster_sizes[i] < 5) continue;
      const int overreach = int(clustered_votes[i] - cluster_sizes[i] * ave_proportional_votes);
      if(overreach > 0) {
        total_overreach += overreach;
      }
      }*/

    // double penalty = pow(total_overreach, popularity_reduction) + 1;
    double orig_total_value = total_value;
    total_value /= pow(raw_score, popularity_reduction);
    //total_value /= penalty;

    if(total_value > top_score) {
      top_score = total_value;
      best_article = article;
    }
    if(raw_score > top_raw) {
      top_raw = raw_score;
      rawest_article = article;
    }
    if(total_value > 0) {
      printf("%.4f %04d %d ", total_value, raw_score, article);
      //printf("%d %.2f ", total_overreach, penalty);
      /*for(int i = 1; i <= max_cluster; i++) {
        printf("%.2f ", cscores[i]);
        }*/
      printf("\n");
    }
  }
  printf("#top score: %.3f %d\n", top_score, best_article);
  printf("#top raw score: %d %d\n", top_raw, rawest_article);

}

Matrix article_scores;

int main(int argc, char* argv[]) {
  Matrix cluster_assignments;
  Matrix votes;

  printf("#command: \"");
  for(int i = 0; i < argc; i++)
    printf("%s ", argv[i]);
  printf("\"\n");


  for(int i = 1; i < argc; i++) {
    if(strcmp(argv[i], "-p") == 0) {
      popularity_reduction = atof(argv[++i]);
    }
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


