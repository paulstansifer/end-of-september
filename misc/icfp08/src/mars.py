from math import *

def dist( (x1, y1), (x2, y2)):
  return sqrt( (x1-x2)**2 + (y1-y2)**2)

def diff_times((x1, y1), (x2, y2), n):
  return ((x1-x2)*n, (y1-y2)*n)

class Rover:
  def configure(self, max_speed):
    self.max_speed = max_speed

rover = Rover()

def angle( (x1, y1), (x2, y2) ):
  return degrees(atan2( (y2-y1), (x2-x1) ))

class Mars:
  def __init__(self):
    self.boulders = []
    self.martians = []
    self.cur_time = -1
    self.tick = 0

  def set_time(self, t):
    self.cur_time = t
    self.tick += 1

  def rec_boulder(self, c, r):
    for b in self.boulders:
      if c == b.c and r == b.r:
        return
    self.boulders.append(Boulder(c, r))

  def rec_martian(self, c, heading, speed):
    for m in self.martians:
      if m.could_be(c, heading, speed):
        m.update(c, heading, speed)
        return
    self.martians.append(Martian(c, heading, speed))

  def total_repel(self, rover_c):
    (dx, dy) = (0, 0)
    for b in self.boulders:
      if dist(rover_c, b.c) < 100:
        bdx, bdy = b.repel(rover_c)
        print "bd ", bdx, bdy
        dx += bdx; dy += bdy;

    for m in self.martians:
      if dist(rover_c, m.c) < 100:
        mdx, mdy = m.repel(rover_c)
        dx += mdx; dy += mdy;

    dist_home = dist(rover_c, (0,0))
    dx -= rover_c[0] / dist_home; dy -= rover_c[1] / dist_home;
  
    return (dx, dy)

  
  def total_occulsion(self, (x,y), rover_dir):
    homeward = degrees(atan2(-y, -x))
    home_dist = dist((x,y), (0,0))
    #TODO: increase temptation of the homeward direction as timelimit approaches ... if we can make it
    #TODO: add a 'stress level' to increase the penalty for turining when danger is near
    
    occl = [-cos(radians(
                   ang_diff(homeward, d)
                   ))  #adjust to face home: [-1.0 .. 1.0]
            + ang_diff(rover_dir, d) / 720 # penalty of up to 0.5 for turning around
                 for d in xrange(0,360)]
    

    if self.tick % 10 == 0:
      print " -------- "
      print " --base-- ", occl[0], occl[90], occl[180], occl[270], occl[315]

    for b in self.boulders:
      if dist( (x,y), b.c) < 200:
        s = b.get_shadow( (x,y) )
        for d in xrange(0,360):
          occl[d] += s(d) #cast shadow

    for m in self.martians:
      if dist( (x,y), m.c) < 200: 
        s = m.get_shadow( (x,y) )
        for d in xrange(0,360):
          occl[d] += s(d) #cast shadow

    if self.tick % 10 == 0:
      print " --adj-- ", occl[0], occl[90], occl[180], occl[270], occl[315]

    return occl

ares = Mars()

def ang_diff(a, b):
  ret_val = abs(a-b)
  if ret_val > 180:
    return 360 - ret_val
  return ret_val


class Boulder:
  def __init__(self, c , r):
    self.c = c; self.r = r;

  def get_shadow(self, c):
    focus = (angle(c, self.c) + 360) % 360
    distance = dist(c, self.c) - 0.5 #count the rover
    if distance <= 0: distance = 0.001 #shouldn't happen, but it does...
    if self.r < distance: #usually true!
      radius = degrees(asin((self.r + .5) / (distance + .5)))
    else:
      radius = 160

    if self.r + 1.0 < distance: #usually true!
      radius_p = degrees(asin((self.r + .5 + 1.0) / (distance + .5)))
    else:
      radius_p = 180
    if radius > 15:
      print "c!", focus, radius, rover.max_speed/distance


    return lambda d : (15/distance * 
             (1 if ang_diff(d, focus) <= radius         #umbra
              else (0.6 if ang_diff(d, focus) <= radius_p #penumbra
              else 0)))

class Martian:
  def __init__(self, c, heading, speed):
    self.max_speed = 0
    self.update(c, heading, speed)

  def update(self, c, heading, speed):
    self.c = c
    self.heading = heading
    self.speed = speed
    if speed > self.max_speed: self.max_speed = speed
    self.last_seen = ares.cur_time

  def could_be(self, c, heading, speed):
    if ares.cur_time == self.last_seen:
      return False
    if dist(c, self.c) / (ares.cur_time - self.last_seen) > max(self.max_speed, speed) * 1.1:
      return False
    return True

  def get_shadow(self, c):

    focus = (angle(c, self.c) + 360) % 360
    co = min(ang_diff(focus, self.heading),
             ang_diff(focus, (self.heading+180) % 360))
    co_coef = (90-co)*4 + 1
    co_coef = 1
    
    distance = dist(c, self.c) - 0.5
    if distance <= 0: distance = 0.001 #shouldn't happen, but it does...

    return lambda d : (5/distance * co_coef/( (co_coef*(ang_diff(d,focus))/15)**2 + 1)
                       if ang_diff(d, focus) < 120 else 0)


