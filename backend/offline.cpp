
#define WANT_STREAM
#define WANT_MATH

#include "external/newmat10/newmatap.h"

#include "external/newmat10/newmatio.h"

#include <iostream>
#include <string>
#include <cstdlib>

using namespace std;

int main(int argc, char* argv[]) {
  int users, articles;
  cin >> users >> articles;
  Matrix key_users(articles, users); //transpose, because there are more articles than users.
  ColumnVector user_means(users);
  key_users = 0; //default: no vote
  int row = -1;
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
      vote_coint++;
      key_users(col, row) = val;
    }
  }
  Matrix ku_U, ku_V;
  DiagonalMatrix D;
  
  cerr << "input complete.\n";
  


  cerr << "Calculating SVD...";
  try{
    SVD(key_users, D, ku_U, ku_V);
  } catch(ProgramException pe) {
    cout << pe.what() << endl;
  }
  cerr << "done.\n";
  
}

