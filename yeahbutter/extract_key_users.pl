#!/usr/bin/perl -w
use Getopt::Long;

sub shuffle(@) {
  for($i = @_-1; $i > 0; $i--) {
    my $loc = int(rand($i + 1));
    my $tmp = $_[$i];
    $_[$i] = $_[$loc];
    $_[$loc] = $tmp;
  }
}


$num_key_users = 500;
$votes_min = -1;
$votes_max = -1;
$shuffling = 0;
$weighting = 0;
$chunk_size = 1000;

$cmd_line = "$0 " . join(' ', @ARGV);

GetOptions(
  'key_users=i' => \$num_key_users,
  'shuffling!' => \$shuffling,
  'weighting!' => \$weighting,
  'min_votes=i' => \$votes_min,
  'max_votes=i' => \$votes_max,
  'chunk_size=i' => \$chunk_size
);

open(LOG, ">", "ex.extraction_log");
print LOG "$cmd_line\n";
#print LOG "key users: $num_key_users\n";
#print LOG "key user vote range: $votes_min < _ < $votes_max\n";
#print LOG "shuffling " . ($shuffling ? "on" : "off") . "\n";
#print LOG "weighting " . ($weighting ? "on" : "off") . "\n";

my $total_votes = 0;
my %votes = ();
my %articles_hash = ();
my %users_hash = ();
my %article_numbers = ();
while(<>) {
  next if(/^\s*$/);
  /^([^|]+)\|([^|]+)/ or warn "incorrectly formatted line: [$_]";
  $user = $2;
  $article = $1;
  $votes{$user}{$article} = 1;
  $articles_hash{$article} = 1;
  $users_hash{$user} = 1;
  $total_votes++;
}
print "input finished\n";
my @users = keys %users_hash;

my %votes_hash;
my @votes;
my @articles = keys(%articles_hash);
my $num_users = @users;
my $num_articles = @articles;
my %key_articles_hash = ();
my %key_users_hash = ();
my $next_key_article_id = 1;
my $next_key_user = 0;
foreach (1 .. $num_key_users) {
#take the first $num_key_users random users
#...but only ones that have enough votes
  do {
    if($next_key_user > $num_users) { die "ran out of users with $votes_min < votes < $votes_max"; }

    $me = $users[$next_key_user++]; 
    %votes_hash = %{ $votes{$me} };
        
    #To be a key user, you must have voted for
    #a reasonable number of articles
  } while(keys %votes_hash < $votes_min or keys %votes_hash > $votes_max);

  $key_users_hash{$me} = 1;
#if($shuffling) {
#   $me = $user_shuffling{$me};
# }
  @votes = keys %votes_hash;
  foreach (@votes) {
    if(!defined($key_articles_hash{$_})) {
      $key_articles_hash{$_} = $next_key_article_id++;
    }
  }
}

print LOG "an estimated " . (100 * $num_key_users / $next_key_user) . "% of users are eligible to be key.\n";
print "an estimated " . (100 * $num_key_users / $next_key_user) . "% of users are eligible to be key.\n";

my @key_users = keys %key_users_hash;
my @key_articles = keys %key_articles_hash;

my ($vote_count, $vote_weight);

if(not $shuffling) {
  open(USER_MAP, ">", "ex.map_users");
  open(ARTICLE_MAP, ">", "ex.map_articles");
  foreach (keys %key_articles_hash) {
    print ARTICLE_MAP  $_, " ", $key_articles_hash{$_}, "\n";
  }
}
open(KEY_USERS, ">", "ex.key_users") or die $!;
my $line = 1;
print STDERR "emitting key users\n";
if($for_newmat) {
  print KEY_USERS "$num_key_users $num_articles\n";
}
foreach (@key_users) {

  print KEY_USERS $line++, " ";
  
  #print KEY_USERS "$_";
  $me = $_;
#  if($shuffling) {
#    $me = $user_shuffling{$me};
#  }
  %votes_hash = %{ $votes{$me} };

  $vote_count = keys %votes_hash;
  $vote_weight = $weighting ? 1.0 / sqrt($vote_count) : 1;
#weighting votes seems to scale up much better
  foreach $article (keys %votes_hash) {
#next if(!defined($key_articles_hash{$article}));
    if($shuffling) {
      print KEY_USERS int(rand(@key_articles))+1; #the valid numbers are packed
        #$articles[int(rand(@articles))];
    } else {
      print KEY_USERS $key_articles_hash{$article};
    }
    print KEY_USERS ":$vote_weight ";
  }
  if($line == 1) {
    #add a dummy article after the end, to make all matrices sized right.
    print @key_articles+1+1 . ":0"
  }
      
  print KEY_USERS "\n";
}

my $user_chunk = 0;
my $user = 0;
open(USER_CHUNK, ">", "ex.users_$user_chunk");
foreach (@users) {
  if($user++ % $chunk_size == 0) {
    close(USER_CHUNK);
    print STDERR "emitting user chunk $user_chunk\n";
    open(USER_CHUNK, ">", "ex.users_$user_chunk") or die $!;
    if($for_newmat) {
      print "$chunk_size $num_articles\n";
    }
    $user_chunk++; 
    $line = 1;
  }
  
  if(not $shuffling) { 
    print USER_MAP "$user $me\n" #emit overall user number
  }
  print USER_CHUNK $line, " ";
  $me = $_;

  %votes_hash = %{ $votes{$me} };
  $vote_count = keys %votes_hash;
  $vote_weight = $weighting ? 1.0 / sqrt($vote_count) : 1;

  foreach $article (keys %votes_hash) {
    next if(!defined($key_articles_hash{$article}));
    if($shuffling) {
      print USER_CHUNK int(rand(@key_articles))+1; #the valid numbers are packed
    } else {
      print USER_CHUNK $key_articles_hash{$article};
    }
    print USER_CHUNK ":$vote_weight ";
  }
  if($line == 1) {
    #add a dummy article after the end, to make all matrices sized right.
    print USER_CHUNK " " . @key_articles+1+1 . ":0";
  }
  
  $line++;
  print USER_CHUNK "\n";
}

print STDERR "emitted " . ($user_chunk) . " chunks.\n";
print LOG "emitted " . ($user_chunk) . " chunks.\n";

