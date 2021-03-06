#!/usr/bin/env python3

import random
import math
import os

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
        time1 = 0
        time2 = 0
        j = 0
        while not (time1 and time2):
            j += 1
            
            # Find a control so that the robots won't hit a wall.
            if time1 == 0:
                intersect = True
                while intersect:
                    ang = random.random() * 2*math.pi
                    dist = 1
                    intersect, dest = r1.motion_model((ang, dist))
                if r1.move(ang, dist):
                    time1 = j
            
            if time2 == 0:
                intersect = True
                while intersect:
                    ang = random.random() * 2*math.pi
                    dist = 1
                    intersect, dest = r2.motion_model((ang, dist))
                if r2.move(ang, dist):
                    time2 = j
            
            print(
                '\r"'+name+'" iteration '+str(i)+
                ', time '+str(j)+
                ', R1: '+str(time1)+
                ', R2: '+str(time2),
                end=''
            )
        
        data.append((time1, time2))
        print('')
    
    return data

def output_data(path, data):
    f = open(path, 'w')
    f.write('R1,R2\n')
    for d in data:
        f.write(str(d[0])+','+str(d[1])+'\n')
    f.close()

# Test parameters
size = [20, 15, 25, 30]
resolution = 0.1

areas = [100, 70, 150]
colours = [8, 5, 12]
walls = [10, 7, 15]

particles = [100, 70, 140, 200]
iterations = 30

data_path = 'data/'

test = {
    'base_case': False,
    'map_size': False,
    'num_areas': False,
    'num_colours': True,
    'num_walls': True,
    'num_particles': False
}

# Test the base case.
name = 'base_case'
if test[name]:
    data = test_case(name, iterations, size[0], resolution, areas[0], colours[0], walls[0], particles[0])
    output_data(data_path+name, data)

# Variable map size.
name = 'map_size'
if test[name]:
    for i in range(1, len(size)):
        n = name+str(size[i])
        data = test_case(n, iterations, size[i], resolution, areas[0], colours[0], walls[0], particles[0])
        output_data(data_path+n, data)

# Variable number of areas.
name = 'num_areas'
if test[name]:
    for i in range(1, len(areas)):
        n = name+str(areas[i])
        data = test_case(n, iterations, size[0], resolution, areas[i], colours[0], walls[0], particles[0])
        output_data(data_path+n, data)

# Variable number of colours.
name = 'num_colours'
if test[name]:
    for i in range(1, len(colours)):
        n = name+str(colours[i])
        data = test_case(n, iterations, size[0], resolution, areas[0], colours[i], walls[0], particles[0])
        output_data(data_path+n, data)

# Variable number of walls.
name = 'num_walls'
if test[name]:
    for i in range(1, len(walls)):
        n = name+str(walls[i])
        data = test_case(n, iterations, size[0], resolution, areas[0], colours[0], walls[i], particles[0])
        output_data(data_path+n, data)

# Variable number of particles.
name = 'num_particles'
if test[name]:
    for i in range(1, len(particles)):
        n = name+str(particles[i])
        data = test_case(n, iterations, size[0], resolution, areas[0], colours[0], walls[0], particles[i])
        output_data(data_path+n, data)
