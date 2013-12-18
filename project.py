#!/usr/bin/env python3

import random
import math
import os

import mapp
import robot

# Load a map, or draw one.
width = 100
height = 100
resolution = 0.25

num_areas = 100
num_colours = 10
num_walls = 10

path = 'map.db'

ma = mapp.Map(width, height, resolution)
if os.path.exists(path):
    ma.load(path)
else:
    ma.fill_floor(num_areas, num_colours)
    ma.save(path)

ma.place_walls(num_walls)

# Initialize the robots and find a good starting point for them.
r1 = robot.Robot1(ma)
r2 = robot.Robot2(ma)

cond = True
while cond:
    x = random.random() * ma.width
    y = random.random() * ma.height
    cond = ma.closest_wall((x, y)) < r1.size

ang = random.random() * 2*math.pi
r1.put(ang, (x, y))
r2.put(ang, (x, y))

# Move the robots around.
r2.draw().save('move-r2/0.png')
for i in range(50):
    print(i)
    r2.move(random.random() * 2*math.pi, 1)
    r2.draw().save('move-r2/test'+str(i+1)+'.png')
