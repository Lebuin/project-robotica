#!/usr/bin/env python3

import math

class Robot:
    
    self.d_sigma = 0.05 # Uncertainty for distances.
    self.a_sigma = math.degrees(0.05) # Uncertainty for angles.
    
    def __init__(self, x, y, ang):
        '''
        Initialize the robot.
        Inputs:
            x: The x-coordinate of the robot.
            y: the y-coordinate of the robot.
            ang: The orientation of the robot in degrees.
        '''
        
        self.x = x
        self.y = y
        self.ang = ang
    
    
    def move(self, dist, ang):
        '''
        Move the robot.
        Inputs:
            dist: The distance over which to move the robot.
            ang: The angle in degrees over which to rotate.
        '''
        
        self.ang += random.gauss(ang, self.a_sigma)
        
        x_move = dist * math.degrees(math.cos(self.ang))
        self.x += random.gauss(x_move, self.d_sigma)
        
        y_move = dist * math.degrees(math.sin(self.ang))
        self.y += random.gauss(y_move, self.d_sigma)
