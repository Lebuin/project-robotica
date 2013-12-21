#!/usr/bin/env python3

import random
import math
import os

import mapp
import robot
import geom

# Test parameters
size = 20
resolution = 0.1

areas = 100
colours = 10
walls = 10

particles = 100
iterations = 30

def test_case(name, iterations, map_size, resolution, num_areas, num_colours, num_walls, num_particles):
    
    data = []
    
    # Do the test iterations times.
    for i in range(1, iterations+1):
        
        # Generate a map.
        ma = mapp.Map(map_size, map_size, resolution)
        ma.fill_floor(num_areas, num_colours)
        ma.place_walls(num_walls)
        
        # Find a good starting point for the robots.
        r1a = robot.Robot1(ma, num_particles)
        r1b = robot.Robot1(ma, num_particles)
        r2a = robot.Robot2(ma, num_particles)
        r2b = robot.Robot2(ma, num_particles)
        
        cond = True
        while cond:
            x = random.random() * ma.width
            y = random.random() * ma.height
            cond = ma.closest_wall((x, y)) < r1a.size
        
        ang = random.random() * 2*math.pi
        r1a.put(ang, (x, y))
        r1b.put(ang, (x, y))
        r2a.put(ang, (x, y))
        r2b.put(ang, (x, y))
        
        # Move the robots until they have found their own location.
        time1a = 1
        time1b = 1
        time2a = 0
        time2b = 0
        j = 0
        while not (time1a and time1b < 0 and time2a and time2b):
            r2a.draw().save('test_move/r2a/'+str(j)+'.png')
            r2b.draw().save('test_move/r2b/'+str(j)+'.png')
            
            j += 1
            
            # Move the random robots:
            if time1a == 0 or time2a == 0:
                
                # Choose the robot that wil be used to find a good control.
                if time1a == 0:
                    r = r1a
                else:
                    r = r2a
                
                # Find a control so that the robots won't hit a wall.
                intersect = True
                while intersect:
                    ang = random.gauss(0, 0.5)
                    dist = 1
                    intersect, dest = r.motion_model((ang, dist))
                
                dist = geom.dist_points(r.coor, dest[1])
                ang = dest[0] - r.ang
                
                if time1a == 0 and r1a.move(ang, dist, exact=True):
                    time1a = j
                if time2a == 0 and r2a.move(ang, dist, exact=True):
                    time2a = j
            
            # Move the self controlled robots.
            if time1b == 0 and r1b.autonome_move():
                time1b = j
            if time2b >= 0 and r2b.autonome_move():
                time2b = j
            
            print(
                '\r"'+name+'" iteration '+str(i)+
                ', time '+str(j)+
                ', time1a: '+str(time1a)+
                ', time1b: '+str(time1b)+
                ', time2a: '+str(time2a)+
                ', time2b: '+str(time2b),
                end=''
            )
        
        data.append((time1a, time1b, time2a, time2b))
        print('')
    
    return data

def output_data(path, data):
    f = open(path, 'w')
    f.write('time1,time2\n')
    for d in data:
        f.write(str(d[0])+','+str(d[1])+'\n')
    f.close()

test_case('part2', 1, 20, 0.1, 100, 10, 10, 100)
