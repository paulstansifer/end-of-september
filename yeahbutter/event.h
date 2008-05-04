#ifndef EVENT_H
#define EVENT_H

/*
 *  event.h
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2007-12-14.
 */


extern double cur_time;

struct event {
  virtual void awake() = 0;
  void put_back();
  double timeout;
};


struct steady_growth : public event {
  steady_growth();
  virtual void awake();
};

struct reddited : public event  {
  virtual void awake();
};

struct analyze : public event {
  analyze();
  virtual void awake();
};

void add_event(event *e);

void initialize_events();

void main_cycle(double max_time);

#endif