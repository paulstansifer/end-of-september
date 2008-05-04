/*
 *  event.cpp
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2007-12-14.
 */

#include "user.h"
#include "event.h"
#include "util.h"
#include <queue>
#include <vector>
#include <iostream>
using namespace std;

double cur_time = 0.0;

struct event_order {
  bool operator()(event* lhs, event* rhs) {
    return lhs->timeout > rhs->timeout; //sort backwards, so the top is the soonest timeout
  }
};

priority_queue<event*, vector<event*>, event_order> events;

void add_event(event *e) {
  events.push(e);
}

void event::put_back() {
  events.push(this);
}

steady_growth::steady_growth() {
  timeout = 5.0;
}

void steady_growth::awake() {
  add_event(new relative_user());
  put_back();
  timeout += 20.0;
}

analyze::analyze() {
  timeout = 30;
}

void analyze::awake() {
  put_back();
  timeout += 30;
  
  advanced_stat user_happiness;
  advanced_stat lifetime_views;
  for(int i = 0; i < registry.size(); i++) {
    int views = registry[i]->views;
    double total_sat = registry[i]->total_satisfaction;
    lifetime_views.record(views);
    if(views > 0)
      user_happiness.record(total_sat / views);
  }
  
  cerr << "[t = " << cur_time << " (: [" << user_happiness.summarize() << "]]" << endl;
  cerr << "[    " << cur_time << " v: [" << lifetime_views.summarize() << "]]" << endl;
}

void reddited::awake() {
}

void initialize_events() {
  events.push(new steady_growth());
  events.push(new analyze());
}

void main_cycle(double max_time) {
  while(cur_time < max_time && !events.empty()) {
    cur_time = events.top()->timeout;
    events.top()->awake();
    events.pop();
  }
}