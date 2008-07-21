from math import *

def dist( (x1, y1), (x2, y2)):
  return sqrt( (x1-x2)**2 + (y1-y2)**2)

class Rover:
  def configure(self, max_speed):
    self.max_speed = max_speed

def angle( (x1, y1), (x2, y2) ):
  return degrees(atan2( (y2-y1), (x2-x1) ))

# Controller's representation of the Martian environment
class Mars:
  def __init__(self):
    # No need to treat boulders and craters separately; we want to avoid both
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
    self.martians.append(Martian(self, c, heading, speed))

  def total_occulsion(self, (x,y), rover_dir):
    homeward = degrees(atan2(-y, -x))
    home_dist = dist((x,y), (0,0))
    
    occl = [-cos(radians(
                   ang_diff(homeward, d)
                   ))  #adjust to face home: [-1.0 .. 1.0]
            + ang_diff(rover_dir, d) / 720 # penalty of 0-0.5 for turning around
                 for d in xrange(0,360)]

    if self.tick % 10 == 0:
      print " -------- "
      print " --base-- ", ' '.join([('%.2f' % occl[a])
                                    for a in range(0, 360, 60)])

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
      print " --adj-- ", ' '.join([('%.2f' % occl[a])
                                    for a in range(0, 360, 60)])

    return occl

def ang_diff(a, b):
  ret_val = abs(a-b)
  if ret_val > 180:
    return 360 - ret_val
  return ret_val

class Boulder:
  def __init__(self, c, r):
    self.c = c
    self.r = r

  def get_shadow(self, c):
    focus = angle(c, self.c) % 360
    distance = dist(c, self.c) - 0.5 #count the rover
    if distance <= 0: distance = 0.001 #shouldn't happen, but it does...
    if self.r < distance: #usually true!
      radius = degrees(asin((self.r + .5) / (distance + .5)))
    else:
      radius = 185

    if self.r + 1.0 < distance: #usually true!
      radius_p = degrees(asin((self.r + .5 + 1.0) / (distance + .5)))
    else:
      radius_p = 185
    if radius > 15:
      print "c!", focus, radius

    def shadow_fun(d):
      if ang_diff(d, focus) <= radius: return 12/distance #umbra
      if ang_diff(d, focus) <= radius_p: return 6/distance #penumbra
      return 0
    return shadow_fun

class Martian:
  def __init__(self, planet, c, heading, speed):
    self.planet = planet
    self.max_speed = 0
    self.update(c, heading, speed)

  def update(self, c, heading, speed):
    self.c = c
    self.heading = heading
    self.speed = speed
    if speed > self.max_speed: self.max_speed = speed
    self.last_seen = self.planet.cur_time

  def could_be(self, c, heading, speed):
    if self.planet.cur_time == self.last_seen:
      return False
    if dist(c, self.c) / (self.planet.cur_time - self.last_seen) > max(self.max_speed, speed) * 1.1:
      return False
    return True

  def get_shadow(self, c):
    focus = angle(c, self.c) % 360
    co = min(ang_diff(focus, self.heading),
             ang_diff(focus, self.heading+180))
    co_coef = (90-co)*4 + 1
    co_coef = 1
    
    distance = dist(c, self.c) - 0.5
    if distance <= 0: distance = 0.001 #shouldn't happen, but it does...

    def shadow_fun(d):
      ad = ang_diff(d, focus)
      if ad < 120:
        return 5/distance * co_coef/((co_coef*ad/15)**2 + 1)
      return 0
    return shadow_fun
