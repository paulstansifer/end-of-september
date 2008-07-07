#ifndef USER_H
#define USER_H

/*
 *  user.h
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2007-11-04.
 */

#include <vector>
#include <fstream>
using namespace std;

#include "event.h"

class post;
class user;

extern vector<user*> registry;
extern unsigned int users_ever;
extern fstream vote_record;


double rnd_double();
void upvote(user*, post*);

class user : public event {
public:  
  int ID;
  
  double activity_delay;
  
  double slant;
  
  double p_a, p_b, p_c;
  double p_slant, p_length;
  
  double skills;
  
  int views;
  double total_satisfaction;

  bool quit;
  
  user();
  
  virtual post * create();
  post * request_next();
  
  virtual bool view(post * p) = 0;
  virtual void awake();
  virtual double evaluate(post * p);
};

class relative_user : public user {
public:
  double expectation;
  
  relative_user();
  
  virtual bool view(post * p);
};

class validation_user : public user {
public:
  int clust_id;
  double x, y;
  validation_user(double clust_x, double clust_y, int clust_id);
  
  virtual bool view(post *) {return true;};
};

//void populate_clustered_validation_users();
void populate_seed_users();
void init_users();


#endif
