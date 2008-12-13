
#define WANT_STREAM
#define WANT_MATH

#include "external/newmat10/newmatap.h"

#include "external/newmat10/newmatio.h"

#include <iostream>
#include <string>
#include <cstdlib>
#include <math.h>

using namespace std;

void normalize_rows(Matrix & m) {
  const int rows = m.Nrows();
  const int cols = m.Ncols();
  for(int i = 1; i <= rows; i++) {
    // cerr << "avg: " << m.Row(i).Sum() / cols
    //      << " sdv: " << sqrt(m.Row(i).SumSquare() / cols) << endl;
    double avg = m.Row(i).Sum() / cols;
    if(avg < 0.00000001) //good enough for an epsilon, when the values are integers
      continue;
    m.Row(i) -= avg;
    double stddev = sqrt(m.Row(i).SumSquare() / cols); //easy to calculate, when mean is 0
    m.Row(i) /= stddev;
    // cerr << "avg: " << m.Row(i).Sum() / cols
//          << " sdv: " << sqrt(m.Row(i).SumSquare() / cols) << endl;
   }
}


int main(int argc, char* argv[]) {
  int users, articles;
  cin >> users >> articles;
  Matrix key_users(articles, users); //transpose, because there are more articles than users.
  ColumnVector user_means(users);
  key_users = 0; //fill with zeros for non-votes
  int row = -1;
  cerr << "reading input...";
  while(!cin.eof()) {
    string token;
    cin >> token;
    //we assume that no column will be repeated
    //int vote_count = 0; //for normalizing

    size_t colon_loc = token.find(':');
    if(colon_loc == string::npos) {
      row = atoi(token.c_str());
      //vote_count = 0;

      cerr << ".";
      cerr.flush();
    } else {
      const int col = atoi(token.substr(0,           colon_loc   )
                             .c_str());
      const int val = atoi(token.substr(colon_loc+1, string::npos)
                             .c_str());
      //vote_count++;
      key_users(col, row) = val;
    }
  }
  cerr << "done.\n";

  if(key_users.Ncols() < 15) {
    cerr << setw(6) << setprecision(2) << key_users.Rows(1,40) << endl;
  }
  
  cerr << "normalizing...";
  normalize_rows(key_users);
  cerr << "done.\n";

  if(key_users.Ncols() < 15) {
    cerr << setw(6) << setprecision(2) << key_users.Rows(1,40) << endl;
  }

  Matrix ku_U, ku_V;
  DiagonalMatrix D;
  

  cerr << "calculating SVD...";
  try{
    SVD(key_users, D, ku_V, ku_U);
    //the sense of V and U are swapped because key_users was
    //transposed. this is because the library requires the matrix to
    //have no more columns than rows.
  } catch(ProgramException pe) {
    cout << pe.what() << endl;
    return 1;
  }
  /*
  cerr << "done.\n";
  cerr << setw(6) << setprecision(2) << D << endl;

  if(key_users.Ncols() < 15) {
    cerr << setw(6) << setprecision(2) << ku_U << endl << endl;
    cerr << setw(6) << setprecision(2) << ku_V.Rows(1,40) << endl;
  }
  */
}

