#!/usr/bin/env python3

import math
import random

class Robot:
    
    d_sigma = 0.05 # Uncertainty for distances.
    a_sigma = 0.05 # Uncertainty for angles.
    num_particles = 100
    
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
        
        # Initialize particles.
        
    
    def motion_model(self, u, state):
        '''
        Calculate the next state for a given state and control.
        Inputs:
            u: A tuple of the form (angle, distance) describing the
                desired movement.
            state: A tuple of the form (angle, x_coordinate,
                y_coordinate) describing the current state.
        Output:
            A tuple of the form (angle, x_coordinate, y_coordinate).
        '''
        
        ang = state[0] + random.gauss(u[0], self.a_sigma)
        dist = random.gauss(u[1], u[1] * self.d_sigma)
        x = state[1] + dist * math.cos(ang)
        y = state[2] + dist * math.sin(ang)
        
        return (ang, x, y)
    
    
    def move(self, ang, dist):
        '''
        Move the robot. A rotation is executed first, and then a
        translation.
        Inputs:
            ang: The angle over which to rotate the robot.
            dist: The distance over which to move the robot.
        '''
        
        # Use the motion model to calculate the next state.
        self.ang, self.x, self.y = self.motion_model(
            (ang, dist),
            (self.ang, self.x, self.y)
        )
        
        
    
    
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
