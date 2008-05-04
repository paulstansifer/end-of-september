use IPC::Open2;

#local (*FRONT, *BACK);
my($front, $back);
#open2(\*FRONT, \*BACK, "date");#"/bin/sh wed.sh");
open2($front, $back, "/bin/sh");

while(<BACK>) {
  print FRONT $_;
  print "around: $_\n";
}

close(FRONT); close(BACK);