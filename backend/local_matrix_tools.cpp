#include "local_matrix_tools.h"

#include <vector>

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
  vector<string> entries;

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
    entries.push_back(token);
  }

  m.resize_keep(max(rows,m.nrows()), max(cols,m.ncols()));

  row = -1;

  for(unsigned i = 0; i < entries.size(); i++) {
    
    string token = entries[i];

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
  vector<int> values;

  int width = 0, height = 1;

  in.getline(line, MAX_LINE);
  char *token = strtok(line, " ");

  while(token != NULL) {
    int val = atoi(token);
    values.push_back(val);
    width++;
    token = strtok(NULL, " ");
  }

  while(!in.eof()) {
    int val;
    in >> val;
    values.push_back(val);
  }

  height = values.size() / width;

  m.ReSize(height, width);

  int idx = 0;
  for(int x = 1; x <= width; x++) {
    for(int y = 1; y <= height; y++) {

      m(y,x) = values[idx++];
    }
  }
}
