#!/usr/bin/env python3

import math
import random

class Robot:
    
    d_sigma = 0.05 # Uncertainty for distances.
    a_sigma = 0.05 # Uncertainty for angles.
    
    def __init__(self, ang, x, y):
        '''
        Initialize the robot.
        Inputs:
            ang: The orientation of the robot in radians.
            x: The x-coordinate of the robot in meters.
            y: the y-coordinate of the robot in meters.
        '''
        
        self.x = x
        self.y = y
        self.ang = ang
    
    
    def move(self, ang, dist):
        '''
        Move the robot. A rotation is executed first, and then a
        translation.
        Inputs:
            ang: The angle over which to rotate the robot.
            dist: The distance over which to move the robot.
        '''
        
        # Rotate the robot with gaussian distribution.
        self.ang += random.gauss(ang, self.a_sigma)
        
        # Move the robot.
        move = random.gauss(dist, self.d_sigma * dist)
        self.x += move * math.cos(self.ang)
        self.y += move * math.sin(self.ang)
        
    
    
    def print(self):
        '''
        Print info on the location of the robot.
        '''
        
        print('angle: ' + str(round(self.ang, 2)) +
            ', coordinates: ('+str(round(self.x, 2)) +
            ', ' + str(round(self.y, 2)) + ')')


class Robot1(Robot):
    
    pass


class Robot2(Robot):
    
    pass
