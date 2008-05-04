/*
 *  dummy.cpp
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2007-11-26.
 *
 */

#include "dummy.h"
#include "post.h"
#include <iostream>
#include <string>
#include <queue>
#include <map>
#include <ext/functional>

unsigned int nextID = 0;

using namespace std;

__gnu_cxx::subtractive_rng rnd;
double rnd_double(){
  return rnd((int)1e8)/1.0e8;
}


void upvote(int, int);

bool use_ranks = false;

struct annotated_post : public post {
  annotated_post() : post() {}
  int votes;  
};

vector<annotated_post*> post_pile;
map<int, annotated_post*> post_index;

int get_a_post();

int main (int argc, char * const argv[]) {
  cerr 
    << "USAGE: " << argv[0] << " <flags>\n"
    << "flags:\n"
    << "  r: use rankings\n";
  if(argc > 1) {
    char* arg = argv[1];
    while(*arg) {
      if(*arg == 'r')
        use_ranks = true;
      arg++;
    }
  }
  string action;
  int user, post;
  while(!cin.eof()) {
    cin >> action;
    if(action == string("UP")) {
      cin >> user >> post;
      upvote(user, post);
    } else if(action == string("POST")) {
      annotated_post * p = new annotated_post(); //the 0-arg constructor grabs from STDIN.
                                                //Hackish, to be sure.
      post_pile.push_back(p);
      post_index[p->ID] = p;
      p->votes = 0;
    } else if(action == string("GET")) {
      cin >> user; //actually, we don't care, because we're the dummy analyzer
      cout << get_a_post() << endl;
    } else if(action == string("QUIT")) {
      break;
    } else {
      break;
    }
  }
  
  return 0;
}

//watch as the master crafts a beautiful selection algorithm, operating
//under only one constraint: to be as easy to implement as possible.
int cur_position = 0;
int sub_position = 0;
inline void advance() {
  if(use_ranks) {
    if(sub_position > post_pile[cur_position]->votes) {
      sub_position = 0;
      cur_position--;
      if(cur_position < 0)
        cur_position = post_pile.size()-1;
    } else {
      sub_position++;
    }
  } else {
    cur_position--;
    if(cur_position < 0)
      cur_position = post_pile.size()-1;
  }    
}

int get_a_post() {
  double choice = rnd_double();
  if(choice < 0.05) { //every once in a while, to keep results fresh
    cur_position = post_pile.size()-1; //reset to the start
    sub_position = 0;
  }
  for(int i = 0; i < 8*choice + 1; i++)
    advance();
  return post_pile[cur_position]->ID;
}

//we ought to, kind of, keep track of who we've told what so we don't double up someone with a post

void upvote(int user, int post) {
  if(post_index.find(post) != post_index.end())
    post_index[post]->votes++;
  else
    cerr << "tried to upvote nonexistent post" << endl;
}
