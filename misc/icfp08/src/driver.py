import socket
#from Tkinter import *
from mars import *
from math import *
import sys

def dturn(s):
  if s == 'L':
    return -hard_turn
  elif s == 'l':
    return -soft_turn
  elif s == '-':
    return 0
  elif s == 'r':
    return soft_turn
  elif s == 'R':
    return hard_turn

#TODO: calculate momentum and figure it out
def r_inertia():
  return .2

def move(turn, urgency=1):
  if turn > 180: turn -= 360
  elif turn < -180: turn += 360

  turn = -turn

  comm = ''

  if abs(turn)*(1+urgency) > 90:
    comm += 'b'
  elif abs(turn)*(1+urgency) < 75:
    comm += 'a'

  #TODO: record fishtailing
  if turn_state == 'R' and turn < hard_turn * r_inertia():
    comm += 'l'; print 'uhr'
  elif turn_state == 'L' and turn > -hard_turn * r_inertia():
    comm += 'r'; print 'uhl'
  elif turn_state == 'r' and turn < soft_turn * r_inertia():
    comm += 'l'; print 'ur'
  elif turn_state == 'l' and turn > -soft_turn * r_inertia():
    comm += 'r'; print 'ul'
  elif turn < -soft_turn / 2:
    comm += 'l'; #print 'gl',
  elif soft_turn / 2 < turn:
    comm += 'r'; #print 'gr',

  print int(turn), comm,

  comm += ';'

  s.send(comm)
  
def process_repulsion((dx, dy)):
  turn = degrees(atan2(dy, dx)) - next_heading

  move(turn)

def process_occlusion(occl):
  best_occl = 999
  best_idx = 0
  for i in xrange(0,360):
    if occl[i] < best_occl:
      best_occl = occl[i]
      best_idx = i

  if best_occl > 1:
    print "BEST: ", best_occl, best_idx
    print occl
    print "H", heading, "NH", next_heading, "I", best_idx

  #print best_occl,
  urgency = occl[int(next_heading) % 360] - best_occl
  #print next_heading, heading, best_idx,
  turn = best_idx - next_heading
  move(turn)
  
    
def rotate((x,y), deg):
  return (x*sin(radians(deg)), y*cos(radians(deg)))
  
def inside_vision((x,y)):
  return False #TODO


#root = Tk()
#root.title('mars')

#canvas = Canvas(root, width=500, height=500)


#root.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) == 3:
  s.connect((sys.argv[1], int(sys.argv[2])))
else:
  s.connect(('localhost', 17676))

s.send('a;')
data = s.recv(1024).split(' ')
if data[0] != 'I': print "What? ", data
xsize = float(data[1])
ysize = float(data[2])
time_limit = float(data[3]) / 1000
min_sensor = float(data[4])
max_sensor = float(data[5])
max_speed = float(data[6]); rover.configure(max_speed)
soft_turn = float(data[7])
hard_turn = float(data[8])
print "size: ", xsize, "x", ysize, " time_limit: ", time_limit
print "sensor: ", min_sensor, "-", max_sensor, " speed: ", max_speed
print "turning: ", soft_turn, "-", hard_turn

heading = 0
turn_state = '-'
move_state = '-'
next_heading = 0
turning_momentum = 0
run = 0

while 1:
  #ignore all but the most recent message.  All we really care about is T anyways
  #(the last thing from split is the empty message after the ';')
  data = s.recv(1024).split(';')[-2].split(' ')
  
  if data[0] == 'T':
    last_heading = heading
    ares.set_time(float(data[1]) / 1000)
    move_state = data[2][0]
    turn_state = data[2][1]
    x = float(data[3])
    y = float(data[4])
    heading = float(data[5])
    speed = float(data[6])

    turning_momentum = heading - last_heading
    next_heading = heading + turning_momentum
    ##TODO: figure out rotational acclr
    #next_heading = heading + dturn(turn_state) * 0.1
    
    i = 7
    while i+1 < len(data):
      obj_type = data[i]
      if obj_type == 'b' or obj_type == 'c':
        ares.rec_boulder( (float(data[i+1]), float(data[i+2])),
                     float(data[i+3]))
        i += 4
      elif obj_type == 'm':
        ares.rec_martian( (float(data[i+1]), float(data[i+2])),
                     float(data[i+3]), float(data[i+4]))
        i += 5
      elif obj_type == 'h':
        #we already know where it is!
        i += 4
      elif obj_type == ';':
        break;
      else:
        print "AIIIIEEE [" + obj_type + "]"
        sys.exit()
    #process_repulsion(ares.total_repel((x,y)))
    process_occlusion(ares.total_occulsion( (x,y), heading))
  elif data[0] == 'E':
    ares.martians = []
    run += 1
    if run >= 5:
      s.close()
      sys.exit()
  #else:
  #  print data
    
  
#  conn.send('a;')

#conn.close()
