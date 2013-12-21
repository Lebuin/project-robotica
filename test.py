#!/usr/bin/env python3

import random
import math
import os

import mapp
import robot
import geom

# Load a map, or draw one.
width = 20
height = 20
resolution = 0.1

num_areas = 100
num_colours = 10
num_walls = 10
len_walls = 15

num_particles = 100

# Make a map.
ma = mapp.Map(width, height, resolution)
path = 'map.db'
if os.path.exists(path):
    ma.load(path)
else:
    ma.fill_floor(num_areas, num_colours)
    ma.save(path)
ma.place_walls(num_walls, len_walls)

# Initialize the robots and find a good starting point for them.
r = robot.Robot1(ma, num_particles)

cond = True
while cond:
    x = random.random() * ma.width
    y = random.random() * ma.height
    cond = ma.closest_wall((x, y)) < r.size

ang = random.random() * 2*math.pi
r.put(ang, (x, y))

# Move the robot around.
r.draw().save('test_move/0.png')
for i in range(1, 1001):
    print(i)
    
    intersect = True
    while intersect:
        ang = random.gauss(0, 0.5)
        dist = 1
        intersect, dest = r.motion_model((ang, dist))
    
    dist = geom.dist_points(r.coor, dest[1])
    ang = dest[0] - r.ang
    r.move(ang, dist, exact=True)
    r.draw().save('test_move/'+str(i)+'.png')
