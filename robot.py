#!/usr/bin/env python3

import math
import random

import mapp
import geom

class Robot:
    
    d_sigma = 0.05 # Uncertainty for distances.
    a_sigma = 0.05 # Uncertainty for angles.
    size = 0.2 # Size of the robot in meters.
    
    ang = 0
    coor = (0, 0)
    
    num_particles = 100
    particles = []
    
    def __init__(self, mapp):
        """
        Initialize the robot with a map.
        Inputs:
            mapp: a Map object on which the robot will move.
        """
        
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
        """
        Put the robot on a place on the map.
        Inputs:
            ang: The orientation of the robot in radians.
            x: The x-coordinate of the robot in meters.
            y: the y-coordinate of the robot in meters.
        """
        
        self.ang = ang
        self.coor = coor
    
    def intersects(self, position, wall):
        """
        Checks if the wall intersects the robot at a given position.
        Inputs:
            state: A tuple with the robot coordinates: (x, y).
            wall: A tuple with the wall's begin and end points:
                ((x1, y1), (x2, y2))
        Output:
            True if the wall intersects the robot, False otherwise.
        """
        
        return geom.dist_point_line(position, wall) < self.size
    
    def motion_model(self, u, state=None):
        """
        Calculate the next state for a given state and control.
        Inputs:
            u: A tuple of the form (angle, distance) describing the
                desired movement.
            state: A tuple of the form (angle, (x_coordinate,
                y_coordinate)) describing the current state.
        Output:
            A tuple of the form (angle, x_coordinate, y_coordinate).
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            ang = self.ang
            coor = self.coor
        else:
            ang = state[0]
            coor = state[1]
        
        #    state = (self.ang, self.coor)
        #x = state[1][0]
        #y = state[1][1]
        
        # Calculate the angle and distance under which to move.
        ang += random.gauss(u[0], self.a_sigma)
        dist = random.gauss(u[1], u[1] * self.d_sigma)
        
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
                coor[0] + step * x_step,
                coor[1] + step * y_step
            )
            
            # Check if the robot collides with any of the walls. If so,
            # make sure we exit the while-loop.
            for wall in self.mapp.walls:
                if self.intersects(position, wall):
                    intersect = True
                    step -= 1
                    break
        
        # Calculate the final position of the robot and return this.
        x = coor[0] + step * x_step
        y = coor[1] + step * y_step
        
        return (ang, (x, y))
    
    def move(self, ang, dist):
        """
        Move the robot according to the motion model and update the
        particles.
        Inputs:
            ang: The angle over which to rotate the robot.
            dist: The distance over which to move the robot.
        """
        
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
        """
        Print info on the location of the robot.
        """
        
        print('angle: ' + str(round(self.ang, 2)) +
            ', coordinates: ('+str(round(self.coor[0], 2)) +
            ', ' + str(round(self.coor[1], 2)) + ')')


class Robot1(Robot):
    
    half_measures = 25  # Half of the number of measurements (the total
                        # number must be even to simplify calculations.)
    max_range = 10  # The maximal measuring distance.
    hit_sigma = 0.05  # See Thrun p. 172. This must be multiplied by
                      # the distance of the measurement.
    
    def measure(self, state=None):
        """
        Do a range scan around a location on the map.
        Inputs:
            state: A tuple of the form (angle, (x, y)) describing the
                robot location.
        Output:
            An array with at most half_measures*2 measurements.
            Measurements are of the form (relative angle, distance) and
            incorporate noise.
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            ang = self.ang
            coor = self.coor
        else:
            ang = state[0]
            coor = state[1]
        
        measurements = []
        
        # Do range_resolution measurements at uniform angles.
        for i in range(self.half_measures):
            theta = math.pi * i / self.half_measures
            real_angle = random.gauss(ang + theta, self.a_sigma)
            beam = (
                coor, (
                    coor[0] + math.cos(real_angle),
                    coor[1] + math.sin(real_angle)
                )
            )
            
            # Loop through all the walls, and see if the beam hits them.
            # We will do this in both positive and negative direction,
            # so at the end of the loop we have the distances to the
            # closest wall on either side of the robot.
            pos_dist = self.max_range
            neg_dist = -self.max_range
            for wall in self.mapp.walls:
                
                # Find the parameters for which the beam and the wall
                # intersect.
                t1, t2 = geom.intersect_lines(beam, wall)
                
                # If t2 lies between 0 and 1, the beam hits the wall
                # at a distance equal to t1.
                if t2 >= 0 and t2 <= 1:
                    if t1 > 0 and t1 < pos_dist:
                        pos_dist = t1
                    elif t1 < 0 and t1 > neg_dist:
                        neg_dist = t1
            
            # Add a noised version of both measurements to the list if
            # they are valid.
            if pos_dist < self.max_range:
                measurements.append((
                    theta,
                    random.gauss(pos_dist, self.d_sigma * pos_dist)
                ))
            if neg_dist > -self.max_range:
                measurements.append((
                    theta - math.pi,
                    random.gauss(-neg_dist, self.d_sigma * pos_dist)
                ))
            
        return measurements
    
    def measurement_model(self, measurements, state=None):
        """
        Calculate the probability of a given range scan for a robot
        location.
        Inputs:
            measurements: An array of measurements, as returned by
                self.measure.
            state: A tuple of the form (angle, (x, y)) describing the
                robot location.
        Output:
            The probability of the scan.
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            ang = self.ang
            coor = self.coor
        else:
            ang = state[0]
            coor = state[1]
        
        prob = 1
        sqrt2pi = math.sqrt(2*math.pi)  # Repeatedly used constant
        
        # Calculate the probability of each measurement and multiply
        # them in prob.
        for meas in measurements:
            x = coor[0] + meas[1] * math.cos(ang + meas[0])
            y = coor[1] + meas[1] * math.sin(ang + meas[0])
            d = self.mapp.closest_wall((x, y))
            
            # Multiply the total measurement probability by the 
            # probability of this measurement, using a Gauss function
            # with mean 0 and std dev hit_sigma * distance.
            sigma = self.hit_sigma * meas[1]
            prob *= math.exp(-d**2 / (2*sigma**2)) / (sigma*sqrt2pi)
            
        return prob


class Robot2(Robot):
    
    def measure(self, state=None):
        """
        Measure the colour of the floor under the robot.
        Inputs:
            state: The location of the robot as a tuple (angle, (x, y)).
        Output:
            The value of the colour of the floor.
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            coor = self.coor
        else:
            coor = state[1]
        
        return self.mapp.get_coordinate(coor)
    
    def measurement_model(self, measurement, state=None):
        """
        Calculate the probability of a measurement at a location of the
        robot.
        Inputs:
            measurement: A value representing the measured color of the
                floor.
            state: The location of the robot as a tuple (angle, (x, y)).
        Output:
            The probability of the measurement.
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            coor = self.coor
        else:
            coor = state[1]
        
        if self.mapp.get_coordinate(coor) == measurement:
            return 1
        else:
            return 0
