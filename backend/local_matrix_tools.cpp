#include "local_matrix_tools.h"

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
    //      << " sdv: " << sqrt(m.Row(i).SumSquare() / cols) << endl;
   }
}

int max(int a, int b) { return a > b ? a : b; }

//Note: you can call this repeatedly to read more values into a matrix.
void read_sparse_matrix(Matrix & m, istream & in) {
  int rows=-1, cols=-1;

  int row = -1;
  while(!in.eof()) {
    string token;
    in >> token;
    size_t colon_loc = token.find(':');
    if(colon_loc == string::npos) {
      row = atoi(token.c_str()); //a token without a column starts a new row
      rows = max(row, rows);
    } else {
      const int col = atoi(token.substr(0, colon_loc).c_str());
      cols = max(col, cols);
    }
  }

  in.seekg(0, ios::beg);

  m.resize_keep(max(rows,m.nrows()), max(cols,m.ncols()));

  row = -1;

  while(!in.eof()) {
    string token;
    in >> token;

    size_t colon_loc = token.find(':');
    if(colon_loc == string::npos) {
      row = atoi(token.c_str()); //a token without a column starts a new row

      //cerr << ".";
      //cerr.flush();
    } else {
      const int col = atoi(token.substr(0,           colon_loc   )
                             .c_str());
      const int val = atoi(token.substr(colon_loc+1, string::npos)
                             .c_str());
      m(row, col) = val;
    }
  }
}

void read_plain_matrix(Matrix & m, istream & in) {
  const int MAX_LINE = 4096;
  char line[MAX_LINE];
  in.getline(line, MAX_LINE);

  int spaces = 0;
  bool in_a_gap = true;
  for(char * i = line; *i; i++) {
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
  while(!in.eof()) {
    in.getline(line, MAX_LINE);
    if(strlen(line) > 1) { //non-empty lines
      height++;
    }
  }

  in.seekg(0, ios::beg); //go back to the beginning, now that we know the size

  m.ReSize(height, width);

  for(int x = 1; x <= width; x++) {
    for(int y = 1; y <= height; y++) {
      int val;
      in >> val;
      m(y,x) = val;
    }
  }
}
