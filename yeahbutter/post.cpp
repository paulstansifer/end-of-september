/*
 *  post.cpp
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2007-11-04.
 */

#include "post.h"
#include "main.h"
#include "user.h"
#include <vector>
#include <iostream>
using namespace std;

vector<post*> post_list;

post::post(user * author) {
  ID = nextID++;
  this->author = author->ID;
  
  post_list.resize(ID+1);
  post_list[ID] = this;
}

void post::emit() {
  cout << "POST " << ID << endl;
}

post::post() {
  cin >> ID;
}

subj_post::subj_post(double a, double b, double c, double slant, double len, user * author) : post(author) {
  ID = nextID++;
  qual_a = a;
  qual_b = b;
  qual_c = c;
  this->slant = slant;
  length = len;
  this->author = author->ID;
}

subj_post::subj_post() {
  cin >> author >> qual_a >> qual_b >> qual_c >> slant >> length;
}

/*
void subj_post::emit() {
  cout << "POST " << ID << " " << author << " " << qual_a << " " << qual_b 
  << " " << qual_c << " " << slant << " " << length << " " << endl;
}
*/
validation_post::validation_post(user * author, int clust_id) : post(author) {
  this->clust_id = clust_id;
}

post * get_post(unsigned int ID) {
  if(ID >= post_list.size())
    return false;
  return post_list[ID];
}