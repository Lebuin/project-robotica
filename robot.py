#!/usr/bin/env python3

import math
import random
import mapp

class Robot:
    
    d_sigma = 0.05 # Uncertainty for distances.
    a_sigma = 0.05 # Uncertainty for angles.
    size = 0.2 # Size of the robot in meters.
    
    num_particles = 100
    particles = []
    
    def __init__(self, mapp):
        '''
        Initialize the robot with a map.
        Inputs:
            mapp: a Map object on which the robot will move.
        '''
        
        self.mapp = mapp
        
        # Draw num_particles random particles inside the map.
        for i in range(self.num_particles):
            self.particles.append((
                random.random() * 2*math.pi,
                (
                    random.random() * mapp.width,
                    random.random() * mapp.height
                )
            ))
    
    
    def put(self, ang, coor):
        '''
        Put the robot on a place on the map.
        Inputs:
            ang: The orientation of the robot in radians.
            x: The x-coordinate of the robot in meters.
            y: the y-coordinate of the robot in meters.
        '''
        
        self.ang = ang
        self.coor = coor
    
    
    def intersects(self, position, wall):
        '''
        Checks if the wall intersects the robot at a given position.
        Inputs:
            state: A tuple with the robot coordinates: (x, y).
            wall: A tuple with the wall's begin and end points:
                ((x1, y1), (x2, y2))
        Output:
            True if the wall intersects the robot, False otherwise.
        '''
        
        return point_line_dist(position, wall) < self.size
    
    
    def motion_model(self, u, state = None):
        '''
        Calculate the next state for a given state and control.
        Inputs:
            u: A tuple of the form (angle, distance) describing the
                desired movement.
            state: A tuple of the form (angle, (x_coordinate,
                y_coordinate)) describing the current state.
        Output:
            A tuple of the form (angle, x_coordinate, y_coordinate).
        '''
        
        # If no state is given, use the current state of the robot.
        if not state:
            state = (self.ang, self.coor)
        x = state[1][0]
        y = state[1][1]
        
        # Calculate the angle and distance under which to move.
        ang = state[0] + random.gauss(u[0], self.a_sigma)
        dist = random.gauss(u[1], u[1] * self.d_sigma)
        dist = u[1]
        
        # Calculate a step size of at most 0.1, so that the destination
        # will be exactly reached.
        steps = int(math.ceil(dist / 0.1))
        x_step = dist / steps * math.cos(ang)
        y_step = dist / steps * math.sin(ang)
        
        # Take small steps until the destination is reached, or the
        # robot collides with a wall.
        step = 0
        intersect = False
        while step < steps and not intersect:
            
            # Calculate the position after an incremented number of
            # steps.
            step += 1
            position = (
                x + step * x_step,
                y + step * y_step
            )
            
            # Check if the robot collides with any of the walls. If so,
            # make sure we exit the while-loop.
            for wall in self.mapp.walls:
                if self.intersects(position, wall):
                    intersect = True
                    step -= 1
                    break
        
        # Calculate the final position of the robot and return this.
        x += step * x_step
        y += step * y_step
        
        return (ang, (x, y))
    
    
    def measurement_model(self):
        '''
        TODO: not implemented yet.
        '''
        
        return 1
    
    
    def move(self, ang, dist):
        '''
        Move the robot according to the motion model and update the
        particles.
        Inputs:
            ang: The angle over which to rotate the robot.
            dist: The distance over which to move the robot.
        '''
        
        u = (ang, dist)
        
        # Move the robot.
        self.ang, self.coor = self.motion_model(u)
        
        # Initialize the temporary particle list with a dummy particle.
        # Elements are of the form ((ang, (x, y)), weight)
        temp = [((0, (0, 0)), 0)]
        for particle in self.particles:
            new_part = self.motion_model(u, particle)
            weight = self.measurement_model()
            
            temp.append((new_part, temp[-1][1] + weight))
        
        # Remove the dummy particle and empty the particle list.
        temp.pop(0)
        self.particles = []
        max_weight = temp[-1][1]
        
        # Add num_particles new particles to the list, according to the
        # cumulative distribution stored in temp[i][1].
        for i in range(self.num_particles):
            selector = random.random() * max_weight
            
            # Find the largest temporary particle whose cumulative
            # weight is smaller than the random selector.
            k = 0
            while temp[k][1] < selector:
                k += 1
            
            # Add the found particle to the particle list.
            self.particles.append(temp[k][0])
    
    
    def print(self):
        '''
        Print info on the location of the robot.
        '''
        
        print('angle: ' + str(round(self.ang, 2)) +
            ', coordinates: ('+str(round(self.x, 2)) +
            ', ' + str(round(self.y, 2)) + ')')    


def point_line_dist(p0, l):
    '''
    Calculate the distance between a point and a line segment.
    Inputs:
        p0: A tuple with the coordinates of the point: (x, y).
        l: A tuple with the begin and end points of the line segment:
            ((x1, y1), (x2, y2))
    Output:
        The distance between the point and the line segment.
    '''
    
    p1 = l[0]
    p2 = l[1]
    
    # Calculate t so that the projection of p0 on the line is at the
    # point p1 + t*(p2-p1): t = dot(p0-p1, p2-p1) / |p1, p2|**2
    t = ((p0[0]-p1[0]) * (p2[0]-p1[0]) +  (p0[1]-p1[1]) * (p2[1]-p1[1])) / ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
    
    # If t is negatif, p1 is the closest point of the line segment.
    if t < 0:
        return point_dist(p0, p1)
    
    # If t > 1, p2 is the closest point.
    elif t > 1:
        return point_dist(p0, p2)
    
    # Otherwise, the orthogonal projection is the closest point.
    else:
        projection = (
            p1[0] + t * (p2[0]-p1[0]),
            p1[1] + t * (p2[1]-p1[1])
        )
        return point_dist(p0, projection)


def point_dist(a, b):
    '''
    Calculate the distance between two points.
    Inputs:
        a: A tuple (x, y).
        b: Id.
    Output:
        The distance between the two points.
    '''
    
    return math.hypot(b[0]-a[0], b[1]-a[1])

class Robot1(Robot):
    
    pass


class Robot2(Robot):
    
    pass
