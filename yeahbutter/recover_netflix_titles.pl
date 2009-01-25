#!/usr/bin/perl -w
open(MAP_ARTICLES, "<", $ARGV[0]);
open(TITLE_MAP, "<", $ARGV[1]);
open(SCORES, "<", $ARGV[2]);

my %yn;

for(<MAP_ARTICLES>) {
  /^(\d+)\s+(\d+)$/;
  $yn{$2} = int($1);
}

my %titles;

for(<TITLE_MAP>) {
  /^(\d+),(\d+),(.*)$/;
  $title{$1} = "$3 ($2)";
}

for(<SCORES>) {
  chomp;
  if(/^[0-9.]+\s+[0-9]+\s+(\d+)/) {
    print "$_ ".$title{$yn{$1}} . "\n";
  } else {
    print "$_\n";
  }
}
