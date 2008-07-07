/*
 *  user.cpp
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2007-11-04.
 *
 */

//We store two states of voting:  the user likes the article, 
//and the user hasn't liked the article yet.

#include "math.h"
#include <ext/functional>
#include <iostream>

#include "user.h"
#include "post.h"
#include "main.h"

using namespace std;


__gnu_cxx::subtractive_rng rnd;

unsigned int users_ever = 0;
vector<user*> registry;
fstream vote_record;


double rnd_double() {
  return rnd((int)1e8)/1.0e8;
}

double rnd_normal() {
  double accum = 0;
  const int samples = 6; //higher is better quality
  for(int i = 0; i < samples; i++) {
    accum += rnd_double();
  }
  accum -= samples/2.0;
  return accum / sqrt(samples/12.0);
}

void upvote(user* u, post* p) {
  cout << "UP " << u->ID << " " << p->ID << endl;
  vote_record << p->ID << "|" << u->ID << endl;
}

user::user() {
  quit = false;
  ID = nextID++;
  users_ever++;
  if(slanty_users && rnd_double() < 0.3) {  //a left-leaning user base
    slant = rnd_double()*0.7 - 1.0;
  } else {
    slant = rnd_double()*2.0 - 1.0;
    if(fabsf(slant) < 0.4)
      slant = rnd_double()*2.0 - 1.0; //fewer moderates
  }
  p_slant = rnd_double()*0.75 + fabsf(slant)*0.25;
  
  skills = rnd_double();
  cout << "JOIN " << ID << endl;
  cerr << "[new user: " << ID << " skills: " << skills << " ]" << endl;

  
  activity_delay = 1.0 / rnd_double();
  timeout = cur_time; //act immediately

  p_a = rnd_double();
  p_b = rnd_double() * rnd_double();
  p_c = rnd_double() * rnd_double() * rnd_double();

  views = 0;
  total_satisfaction = 0;
  //p_length = (rnd_double() - 0.5) * 0.35;

  registry.push_back(this);
}

double user::evaluate(post * pst) {
  subj_post * p = (subj_post *)pst;
  //slants tend to be high, compared to skills, so we'll tone them down.
  return fabsf(slant - p->slant) * p_slant * 0.4
    + p->qual_a * p_a 
    + p->qual_b * p_b 
    + p->qual_c * p_b;
}

void user::awake() {
  if(rnd_double() < 0.6) { // reading is more likely
    while(rnd_double() < 0.6) {
      post * p = request_next();
      if(p == NULL)
        break;
      quit |= !view(p); //as a side-effect, possibly up-votes
    }
  } else { // %20 chance: write
    create();
  }

  if(!quit){
    timeout += rnd_double() * activity_delay;
    put_back();
  }
}


post * user::create() {
  double post_slant = (rnd_double() - 0.5) * (1-p_slant) * 2 + slant;
  if(post_slant < -1.0) post_slant = -1.0;
  if(post_slant > 1.0) post_slant = 1.0;
  post * ret_val = new subj_post(p_a * skills * rnd_double(),
                  p_b * skills * (1 - rnd_double()*rnd_double()),
                  p_c * skills * (1 - rnd_double()*rnd_double()),
                  post_slant, 0, this);
  //cerr << "@" << cur_time << " ";
  ret_val->emit();
  return ret_val;
}

post * user::request_next() {
  int postID;
  //cerr << "@" << cur_time << " ";
  cout << "GET " << ID << endl;
  cin >> postID;
  if(postID == -1)
    return NULL;
  return get_post((unsigned int)postID);
}

relative_user::relative_user() : user() {
  expectation = rnd_double() * 0.5;
}

bool relative_user::view(post * p) {
  double value = evaluate(p);
  if(value > expectation + fabsf(expectation*0.35) + 0.05)
    upvote(this, p);
  expectation = expectation * 0.75 + value * 0.25;
  
  if(total_satisfaction < -2 || views < -2) {
    cerr << "[Uh, oh!]" << endl;
  }
  total_satisfaction += value;
  views++;

  if(total_satisfaction/views >= 0.1) //Do we want to stay?   
    return true;
  cerr << "[quit: " << ID << "]" << endl;
  return false;
}


validation_user::validation_user(double clust_x, double clust_y, int clust_id) {
  this->clust_id = clust_id;
  cerr << "normal: " << rnd_normal() << endl;
  x = clust_x + rnd_normal()*0.2;
  y = clust_y + rnd_normal()*0.2;
}

void run_validation() {
  init_users();
  for(int i = 0; i < 15; i++) {
    for(int j = 0; j < 20; j++) {
      double x = rnd_normal();
      double y = rnd_normal();
      user * u = new validation_user(x,y,i);
      u->timeout = 10000000.0;
      add_event(u);
    }
  }
  
  //for(int i = 0; i < 1000
}

void init_users() {
  vote_record.open("votes", ios_base::out);
  
}
  

void populate_seed_users() {
  init_users();
  user * u1 = new relative_user();
  u1->skills = 0.7;
  u1->slant = -0.5;
  u1->timeout = 1.0;
  user * u2 = new relative_user();
  u2->skills = 0.7;
  u2->slant = -0.5;
  u2->timeout = 1.0;
  
  u1->create();
  u2->create();
  u1->create();
  u2->create();
  u1->create();
  u2->create();
  u1->create();
  u2->create();
  
  add_event(u1);
  add_event(u2);
}
