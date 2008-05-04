/*
 *  util.h
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2008-01-06.
 *
 */
#include <float.h>
#include <fstream>
#include <vector>
#include <string>
using namespace std;

struct stat{
  double min, max, total;
  int hits;
  
  stat();
  
  virtual void record(double v);
  
  virtual string summarize();
};

struct advanced_stat : public stat {
  vector<double> vals;
  advanced_stat();

  virtual void record(double v);
  
  virtual string summarize();
};
