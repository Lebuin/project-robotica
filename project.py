#!/usr/bin/env python3

import random
import math
import os

import mapp
import robot

# Load a map, or draw one.
width = 30
height = 10
resolution = 0.1

num_areas = 100
num_colours = 10
num_walls = 5

num_particles = 200

path = 'map.db'

ma = mapp.Map(width, height, resolution)
if os.path.exists(path):
    ma.load(path)
else:
    ma.fill_floor(num_areas, num_colours)
    ma.save(path)

ma.place_walls(num_walls)

# Initialize the robots and find a good starting point for them.
r1 = robot.Robot1(ma, num_particles)
r2 = robot.Robot2(ma, num_particles)

cond = True
while cond:
    x = random.random() * ma.width
    y = random.random() * ma.height
    cond = ma.closest_wall((x, y)) < r2.size

ang = random.random() * 2*math.pi
r1.put(ang, (x, y))
r2.put(ang, (x, y))

# Move the robots around.
r1.draw().save('move-r1/test0.png')
for i in range(1000):
    print(i)
    r1.move(random.gauss(0, 1), 1)
    r1.draw().save('move-r1/test'+str(i+1)+'.png')
