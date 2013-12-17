#!/usr/bin/env python3

import math

class Robot:
    
    def __init__(self, x, y):
        '''
        Initialize the robot.
        Inputs:
            x: The x-coordinate of the robot.
            y: the y-coordinate of the robot.
        '''
        
        self.x = x
        self.y = y
    
    
    def move(self, dist, ang):
        '''
        Move the robot.
        Inputs:
            dist: The distance over which to move the robot.
            ang: The angle in degrees with the positive x-axis being 0°.
        '''
        
        self.x += dist * math.degrees(math.cos(ang))
        self.y += dist * math.degrees(math.sin(ang))
