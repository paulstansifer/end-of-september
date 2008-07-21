import socket
from mars import *
from math import *
import sys

def dturn(s):
  return {'L': -hard_turn,
          'l': -soft_turn,
          '-': 0,
          'r': soft_turn,
          'R': hard_turn}[s]

def move(turn, urgency=1):
  if turn > 180: turn -= 360
  elif turn < -180: turn += 360

  turn = -turn

  comm = ''

  if ares.cur_time < 2.5:
    comm += 'a' #in the beginning, pick up speed
  else:
    if abs(turn)*(1+urgency) > 80:
      comm += 'b'
    elif abs(turn)*(1+urgency) < 65:
      comm += 'a'

  r_inertia = 0.2
  if turn_state == 'R' and turn < hard_turn * r_inertia:
    comm += 'l'
  elif turn_state == 'L' and turn > -hard_turn * r_inertia:
    comm += 'r'
  elif turn_state == 'r' and turn < soft_turn * r_inertia:
    comm += 'l'
  elif turn_state == 'l' and turn > -soft_turn * r_inertia:
    comm += 'r'
  elif turn < -soft_turn / 2:
    comm += 'l'
  elif soft_turn / 2 < turn:
    comm += 'r'

  comm += ';'

  s.send(comm)
  
def process_occlusion(occl):
  best_occl = 999
  best_idx = 0
  for i in xrange(0,360):
    if occl[i] < best_occl:
      best_occl = occl[i]
      best_idx = i

  urgency = occl[int(next_heading) % 360] - best_occl
  turn = best_idx - next_heading
  move(turn)

#Initialization before event loop
rover = Rover()
ares = Mars()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
if len(sys.argv) == 3:
  s.connect((sys.argv[1], int(sys.argv[2])))
else:
  s.connect(('localhost', 17676))

s.send('a;')
data = s.recv(1024).split(' ')
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

# Event loop
while True:
  data = s.recv(1024).split(';')[0].split(' ')

  if not data[0] in ('T', 'E'):
    print data
    continue

  if data[0] == 'E':
    ares.martians = []
    continue

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
  process_occlusion(ares.total_occulsion( (x,y), heading))
