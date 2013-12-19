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

num_particles = 100

path = 'map.db'

ma = mapp.Map(width, height, resolution)
if os.path.exists(path):
    ma.load(path)
else:
    ma.fill_floor(num_areas, num_colours)
    ma.save(path)

ma.place_walls(num_walls)

# Initialize the robots and find a good starting point for them.
r = robot.Robot2(ma, num_particles)

cond = True
while cond:
    x = random.random() * ma.width
    y = random.random() * ma.height
    cond = ma.closest_wall((x, y)) < r.size

ang = random.random() * 2*math.pi
r.put(ang, (x, y))

# Move the robots around.
r.draw().save('move-r2/test0.png')
for i in range(1, 1001):
    print(i)
    
    intersect = True
    while intersect:
        ang = random.gauss(0, 1)
        dist = 1
        intersect, _ = r.motion_model((ang, dist))
        #intersect, _, _ = geom.dist_point_point(r.coor, dest[1])
        
        #dest = (
            #r.coor[0] + dist * math.cos(r.ang + ang),
            #r.coor[1] + dist * math.sin(r.ang + ang)
        #)
        #intersect = r.mapp.intersect_wall((r.coor, dest))
    
    r.move(ang, dist)
    r.draw().save('move-r2/test'+str(i)+'.png')
