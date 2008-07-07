#ifndef POST_H
#define POST_H
/*
 *  post.h
 *  yeahbutter
 *
 *  Created by Paul Stansifer on 2007-11-04.
 *
 */

class user;




struct post {
public:
  int ID;
  int author;
  
  post();
  post(user * author);
  void emit();
};

struct subj_post : public post {
public:
  double qual_a, qual_b, qual_c;
  double slant;
  double length;
  
  subj_post(double a, double b, double c, double slant, double len, user * author);
  subj_post();
};

struct validation_post : public post {
public:
  int clust_id;
  validation_post(user * author, int clust_id);
};

post * get_post(unsigned int ID);

#endif
