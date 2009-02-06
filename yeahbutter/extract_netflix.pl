#!/usr/bin/perl -w

#open(VOTES, ">", "netflix_votes");

my %total_score;
my %voters;

@movies = <*>;
for $movie (@movies) {
  ($movie_id) = $movie =~ /mv_(\d+)\.txt/;

  open(MOVIE, "<", $movie);
  for(<MOVIE>) {
    next if(/\d+:/);
    /(\d+),(\d),([-0-9]+)/;
    next if($1 >= 75000);

    #if(not exists $total_score{
    $total_score{$movie_id} += $2;
    $voters{$movie_id} += 1;
    if($2 >= 4) {
      print "$movie_id|$1\n";
    }
  }
}

open(AVERAGE_SCORES, ">", "average_scores");

for (keys %total_score) {
  print AVERAGE_SCORES "$_ " . $total_score{$_} / $voters{$_} . " " . $voters{$_} . "\n";
}
  
#movie | user
