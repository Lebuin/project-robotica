#!/usr/bin/env python3

import random
import math
import os
import sys

import mapp
import robot
import geom

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
        time1a = 0
        time1b = 1
        time2a = 1
        time2b = 1
        j = 0
        
        while not (time1a and time1b and time2a and time2b):
            r1a.draw().save('test_move/r1a/'+str(j)+'.png')
            #r1b.draw().save('test_move/r1b/'+str(j)+'.png')
            #r2a.draw().save('test_move/r2a/'+str(j)+'.png')
            #r2b.draw().save('test_move/r2b/'+str(j)+'.png')
            
            j += 1
            
            # Move the random robots:
            if time1a == 0:
                ang = random.gauss(0, math.pi/3)
                dist = 1
                if r1a.move(ang, dist):
                    time1a = j
            
            if time2a == 0:
                ang = random.gauss(0, math.pi/3)
                dist = 1
                if r2a.move(ang, dist):
                    time2a = j
            
            # Move the self controlled robots.
            if time1b == 0 and r1b.autonome_move():
                time1b = j
            
            if time2b == 0 and r2b.autonome_move():
                time2b = j
            
            print(
                '\r"'+name+'" iteration '+str(i)+
                ', time '+str(j)+
                ', R1a: '+str(time1a)+
                ', R1b: '+str(time1b)+
                ', R2a: '+str(time2a)+
                ', R2b: '+str(time2b),
                end=''
            )
        
        data.append((time1a, time1b, time2a, time2b))
        print('')
    
    return data

def output_data(path, data):
    f = open(path, 'w')
    f.write('R1,R1 (autonome),R2,R2 (autonome)\n')
    for d in data:
        line = ''
        for time in d:
            line += str(time)+','
        f.write(line[:-1]+'\n')
    f.close()

# Test parameters
size = 20
resolution = 0.1

areas = 100
colours = 8
walls = 10

particles = 100
iterations = 1

data = test_case('part2', iterations, size, resolution, areas, colours, walls, particles)
output_data('data/part2', data)
