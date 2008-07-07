/*
 *  util.cpp
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2008-01-06.
 *
 */

#include "util.h"
#include <math.h>


string n(double v) {
  char buf[16];
  snprintf(buf, 16, "%.3f", v);
  return string(buf);
}

string n(int i) {
  char buf[16];
  snprintf(buf, 16, "%d", i);
  return string(buf);
}  

stat::stat() {
  hits = 0;
  min = DBL_MAX;
  max = DBL_MIN;
  total = 0.0;
}

void stat::record(double v) {
  if(v < 0)
    throw 0;
  if(v < min)
    min = v;
  if(v > max)
    max = v;
  total += v;
  hits++;
}

string stat::summarize() {
  return "#: " + n(hits) + " m/m: " + n(min) + "/" + n(max) + " avg: " + n(total/hits);
}

advanced_stat::advanced_stat() : stat() {};
  
void advanced_stat::record(double v) {
  stat::record(v);
  vals.push_back(v);
}

string advanced_stat::summarize() {
  sort(vals.begin(), vals.end());
  if(vals.size() == 0) return "(nothing yet)";
  double q1 = vals[hits/4];
  double med = vals[hits/2];
  double q3 = vals[3*hits/4];
  double mean = total/hits;
  double sum_sq_diff = 0;
  for(int i = 0; i < hits; i++) {
    double diff = fabs(mean - vals[i]);
    sum_sq_diff += diff*diff;
  }
  double std_dev = sqrt(sum_sq_diff / hits);
  
  return "#: " + n(hits) + " m/1/m/3/m: " + n(min) + "/" + n(q1) + "/" + n(med) 
    + "/" + n(q3) + "/" + n(max) + " avg: " + n(mean) + " sd: " + n(std_dev);
}
