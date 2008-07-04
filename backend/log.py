import sys

TEMP = -1 #Too verbose or expensive to leave in code
DEBUG = 0
WARN = 1
ERROR = 2
FATAL = 3 #We must shut down

def log(level, msg):
    if(level >= DEBUG):
        print >> sys.stderr, msg

def log_tmp(msg):
    print >> sys.stderr, msg

def log_dbg(msg):
    print >> sys.stderr, msg

def log_wrn(msg):
    print >> sys.stderr, msg

def log_err(msg):
    print >> sys.stderr, msg

def log_ftl(msg):
    print >> sys.stderr, msg
