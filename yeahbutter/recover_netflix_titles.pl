#!/usr/bin/perl -w
open(MAP_ARTICLES, "<", $ARGV[0]);
open(TITLE_MAP, "<", $ARGV[1]);
open(AVG_SCORES, "<", $ARGV[2]);
open(SCORES, "<", $ARGV[3]);

$pop_penalty = $ARGV[4];

print "#command: $0 @ARGV\n";

my %yn;

for(<MAP_ARTICLES>) {
  /^(\d+)\s+(\d+)$/;
  $yn{$2} = int($1);
}

my %title;

for(<TITLE_MAP>) {
  if(/^(\d+),(\d+),(.*)$/) {
    $title{$1} = "$3 ($2)";
  }
}

my %avg_scores;
my %popularity;

for(<AVG_SCORES>) {
  if(/^(\d+) ([0-9.]+) ([0-9]+)$/) {
    $avg_scores{int($1)} = $2;
    $popularity{int($1)} = $3;
  }
}

for(<SCORES>) {
  chomp;
  if(/^([0-9.]+)\s+(\d+)/) {
    $n = $yn{$2}; #The netflix id of the movie
    $n =~ s/ /_/g;
    $score = sprintf("%.2f", ($1 / $popularity{$n} ** $pop_penalty) * 1000);
    print "$score $n $avg_scores{$n} $popularity{$n}  $title{$n} $_\n";
  } else {
    print "$_\n";
  }
}
