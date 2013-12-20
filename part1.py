#!/usr/bin/env python3

import random
import math
import os

import mapp
import robot
import geom

def test_case(name, iterations, map_size, resolution, num_areas, num_colours, num_walls, len_walls, num_particles):
    
    # Do the test iterations times.
    for i in range(1, iterations+1):
        
        # Generate a map.
        ma = mapp.Map(map_size, map_size, resolution)
        ma.fill_floor(num_areas, num_colours)
        ma.place_walls(num_walls, len_walls)
        
        # Find a good starting point for the robots.
        r1 = robot.Robot1(ma, num_particles)
        r2 = robot.Robot2(ma, num_particles)
        
        cond = True
        while cond:
            x = random.random() * ma.width
            y = random.random() * ma.height
            cond = ma.closest_wall((x, y)) < r1.size
        
        ang = random.random() * 2*math.pi
        r1.put(ang, (x, y))
        r2.put(ang, (x, y))
        
        # Move the robots until they have found their own location.
        found1 = 0
        found2 = 0
        j = 0
        while not (found1 and found2):
            #r1.draw().save('move-r1/test'+str(j)+'.png')
            #r2.draw().save('move-r2/test'+str(j)+'.png')
            
            j += 1
            
            # Choose the robot that wil be used to find a good control.
            if found2 > 0:
                r = r1
            else:
                r = r2
            
            # Find a control so that the robots won't hit a wall.
            intersect = True
            while intersect:
                ang = random.gauss(0, 0.5)
                dist = 1
                intersect, dest = r.motion_model((ang, dist))
            
            dist = geom.dist_points(r.coor, dest[1])
            ang = dest[0] - r.ang
            
            if found1 == 0 and r1.move(ang, dist, exact=True):
                found1 = j
            if found2 == 0 and r2.move(ang, dist, exact=True):
                found2 = j
            
            print(
                '\r"'+name+'" iteration '+str(i)+
                ', time '+str(j)+
                ', found1: '+str(found1)+
                ', found2: '+str(found2),
                end=''
            )
        # Todo: output test data.
        print('')

# Test parameters
map_size = [20, 15, 25, 30]
resolution = 0.1

num_areas = [100, 70, 130, 160, 200]
num_colours = [10, 7, 15]

num_walls = [10, 7, 15]
len_walls = [10, 8, 13, 15, 20]

num_particles = 100

# Test the base case
name = 'base_case'
test_case(name, 2, 20, 0.1, 100, 10, 10, 10, 100)
