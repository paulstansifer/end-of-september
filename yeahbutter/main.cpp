#include <iostream>
#include "main.h"
#include "user.h"
#include "event.h"
using namespace std;

unsigned int nextID = 0;
bool slanty_users = false;
bool static_users = true;
int event_count = 50000;
int main (int argc, char * const argv[]) {
  cerr 
    << "USAGE: yeahbutter <flags> <event_count>\n"
    << "flags:\n"
    << "  l: left-leaning user base\n"
    << "  d: dynamic users (leave if unsatisfied)\n" ;
  if(argc > 2) {
    char* args = argv[1];
    while(args++) {
      if(*args == 'l')
        slanty_users = true;
      else if(*args == 'd')
        static_users = false;
    }
    
    event_count = atoi(argv[2]);
  }
  
  initialize_events();
  populate_seed_users();
  main_cycle(5000.0);
  
  
  return 0;
}
