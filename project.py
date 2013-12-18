#!/usr/bin/env python3

import random
import math

import mapp
import robot

# Draw a map.
width = 100
height = 100
resolution = 0.25

num_areas = 100
num_colours = 10
num_walls = 10

ma = mapp.Map(width, height, resolution)
ma.fill_floor(num_areas, num_colours)
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
for i in range(5):
    r2.move(random.random() * 2*math.pi, 1)
    

ma.draw(robot=r1.coor, particles=r1.particles).save('test.png')
