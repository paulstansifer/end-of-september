#!/usr/bin/perl -w

#open(VOTES, ">", "netflix_votes");

@movies = <*>;
for $movie (@movies) {
  ($movie_id) = $movie =~ /mv_(\d+)\.txt/;

  open(MOVIE, "<", $movie);
  for(<MOVIE>) {
    next if(/\d+:/);
    /(\d+),(\d),([-0-9]+)/;
    next if($1 >= 75000);
    if($2 >= 4) {
      print "$movie_id|$1\n";
    }
  }
}
  
#movie | user
