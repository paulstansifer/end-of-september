#define WANT_STREAM
#define WANT_MATH

//everybody probably wants these here includes
#include "external/newmat11/newmatap.h"
#include "external/newmat11/newmatio.h"

#include <iostream>

using namespace std;

void normalize_rows(Matrix & m);

void read_sparse_matrix(Matrix & m, istream & in);

void read_plain_matrix(Matrix & m, istream & in);
