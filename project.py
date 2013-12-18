#!/usr/bin/env python3

import random
import math

import mapp
import robot

# Draw a map and output it
width = 100
height = 100
resolution = 0.25

num_areas = 100
num_colours = 10
num_walls = 10

ma = mapp.Map(width, height, resolution)
ma.fill_floor(num_areas, num_colours)
ma.place_walls(num_walls)
ma.draw_map('test.png')

# Find a good starting point for the robots:
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
