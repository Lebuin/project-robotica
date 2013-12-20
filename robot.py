#!/usr/bin/env python3

import math
import random

import mapp
import geom

class Robot:
    
    def __init__(self, mapp, num_particles):
        """
        Initialize the robot with a map.
        Inputs:
            mapp: a Map object on which the robot will move.
        """
        
        self.d_sigma = 0.05 # Uncertainty for distances.
        self.a_sigma = 0.05 # Uncertainty for angles.
        self.size = 0.2 # Size of the robot in meters.
        
        self.ang = 0
        self.coor = (0, 0)
        
        self.alp_slow = 0.1
        self.alp_fast = 0.8
        self.w_slow = 1
        self.w_fast = 1
        
        self.alp_dist = 0.5
        self.w_dist = 10
        
        self.num_particles = num_particles
        self.particles = []
        
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
    
    def motion_model(self, u, state=None, exact=False):
        """
        Calculate the next state for a given state and control.
        Inputs:
            u: A tuple of the form (angle, distance) describing the
                desired movement.
            state: A tuple of the form (angle, (x_coordinate,
                y_coordinate)) describing the current state.
        Output:
            A tuple of the form (angle, (x, y)).
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            ang = self.ang
            coor = self.coor
        else:
            ang = state[0]
            coor = state[1]
        
        # Calculate the angle and distance under which to move.
        if exact:
            ang += u[0]
            dist = u[1]
        else:
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
        
        return (intersect, (ang, (x, y)))
    
    def move(self, ang, dist, exact=False):
        """
        Move the robot according to the motion model and update the
        particles.
        Inputs:
            ang: The angle over which to rotate the robot.
            dist: The distance over which to move the robot.
        """
        
        u = (ang, dist)
        
        # Move the robot.
        _, new_state = self.motion_model(u, exact=exact)
        self.ang, self.coor = new_state
        self.measure()
        
        # Initialize the temporary particle list with a dummy particle.
        # Elements are of the form ((ang, (x, y)), weight)
        temp = [((0, (0, 0)), 0)]
        for particle in self.particles:
            _, new_part = self.motion_model(u, particle)
            weight = self.measurement_model(new_part)
            
            temp.append((new_part, temp[-1][1] + weight, weight))
        
        # Remove the dummy particle and empty the particle list.
        temp.pop(0)
        self.particles = []
        rand_particles = []
        total_weight = temp[-1][1]
        self.set_weights(temp)
        
        # Add num_particles new particles to the list, according to the
        # cumulative distribution stored in temp[i][1].
        for i in range(self.num_particles):
            if random.random() < (1 - self.w_fast/self.w_slow/self.w_divider):
                rand_particles.append(self.random_particle())
                
            else:
                selector = random.random() * total_weight
                
                # Find the largest temporary particle whose cumulative
                # weight is smaller than the random selector.
                k = 0
                while temp[k][1] < selector:
                    k += 1
                self.particles.append(temp[k][0])
        
        # See if the non-random particles are close enough yet.
        self.w_dist += self.alp_dist * (self.particles_distance() - self.w_dist)
        self.particles.extend(rand_particles)
        
        if self.w_dist < 0.5:
            return True
        else:
            return False
        
    
    def particles_distance(self):
        """
        Calculate the average distance of the best portion of the
        particles to the actual robot position.
        """
        
        avg_num = self.num_particles//5
        distances = map(lambda p: geom.dist_points(self.coor, p[1]), self.particles)
        return sum(sorted(distances)[:avg_num])/avg_num
    
    def print(self):
        """
        Print info on the location of the robot.
        """
        
        print('angle: ' + str(round(self.ang, 2)) +
            ', coordinates: ('+str(round(self.coor[0], 2)) +
            ', ' + str(round(self.coor[1], 2)) + ')')
    
    def draw(self):
        """
        Draw a map with the robot and current particles on it.
        Output:
            An Image file, from the PIL module.
        """
        
        return self.mapp.draw(
            robot=self.coor,
            particles=self.particles
        )


class Robot1(Robot):
    
    half_measures = 25  # Half of the number of measurements (the total
                        # number must be even to simplify calculations.)
    min_range = 1   # The minimal and
    max_range = 10  # maximal measuring distance.
    hit_sigma = 0.2 # See Thrun p. 172. This must be multiplied by
                     # the distance of the measurement.
    w_divider = 1.5
    
    measurement = []
    
    def set_weights(self, particles):
        """
        Update the moving averages used to determine the number of
        random particles that will be drawn.
        Inputs:
            particles: A list with the temporary particles:
                (coordinate, cumulative weight, weight).
        """
        
        w_avg = 1
        avg_dist = 1
        power = 1/(len(particles)*len(self.measurement))
        total_weight = particles[-1][1]
        for p in particles:
            w_avg *= p[2]**power
            avg_dist *= geom.dist_points(self.coor, p[0][1])**(p[2]/total_weight)
        
        self.w_slow += self.alp_slow * (w_avg - self.w_slow)
        self.w_fast += self.alp_fast * (w_avg - self.w_fast)
    
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
        
        self.measurement = []
        
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
            pos_dist += random.gauss(0, self.d_sigma * pos_dist)
            neg_dist += random.gauss(0, self.d_sigma * neg_dist)
            if pos_dist > 0.5 and pos_dist < self.max_range:
                self.measurement.append((
                    theta,
                    random.gauss(pos_dist, self.d_sigma * pos_dist)
                ))
            if neg_dist < -0.5 and neg_dist > -self.max_range:
                self.measurement.append((
                    theta - math.pi,
                    random.gauss(-neg_dist, self.d_sigma * pos_dist)
                ))
    
    def measurement_model(self, state=None):
        """
        Calculate the probability of a given range scan for a robot
        location.
        Inputs:
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
        for meas in self.measurement:
            x = coor[0] + meas[1] * math.cos(ang + meas[0])
            y = coor[1] + meas[1] * math.sin(ang + meas[0])
            d = self.mapp.closest_wall((x, y))
            
            # Multiply the total measurement probability by the 
            # probability of this measurement, using a Gauss function
            # with mean 0 and std dev hit_sigma.
            p = math.exp(-d**2 / (2*self.hit_sigma**2)) / (self.hit_sigma*sqrt2pi) + 0.01
            
            prob *= p
            
        return prob
    
    def random_particle(self):
        """
        Draw a random particle on the map. Currently this is really
        random, but this could be made better by using information on
        the map.
        """
        
        x = random.random() * self.mapp.width
        y = random.random() * self.mapp.height
        ang = random.random() * 2*math.pi
        return (ang, (x, y))


class Robot2(Robot):
    
    measurement = 0
    w_divider = 1
    
    def set_weights(self, particles):
        """
        Update the moving averages used to determine the number of
        random particles that will be drawn.
        Inputs:
            particles: A list with the temporary particles: 
                (coordinate, cumulative weight, weight).
        """
        
        w_avg = 0
        w_avg = sum([p[2] for p in particles]) / self.num_particles
        
        self.w_slow += self.alp_slow * (w_avg - self.w_slow)
        self.w_fast += self.alp_fast * (w_avg - self.w_fast)
    
    def measure(self, state=None):
        """
        Measure the colour of the floor under the robot.
        Inputs:
            state: The location of the robot as a tuple (angle, (x, y)).
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            coor = self.coor
        else:
            coor = state[1]
        
        self.measurement = self.mapp.get_coordinate(coor)
    
    def measurement_model(self, state=None):
        """
        Calculate the probability of a measurement at a location of the
        robot.
        Inputs:
            state: The location of the robot as a tuple (angle, (x, y)).
        Output:
            The probability of the measurement.
        """
        
        # If no state is given, use the current state of the robot.
        if state is None:
            coor = self.coor
        else:
            coor = state[1]
        
        if self.mapp.get_coordinate(coor) == self.measurement:
            return 1
        else:
            return 0.05
    
    def random_particle(self):
        """
        Draw a random particle on the map. Currently this is really
        random, but this could be made better by using information on
        the map.
        """
        x = random.random() * self.mapp.width
        y = random.random() * self.mapp.height
        ang = random.random() * 2*math.pi
        return (ang, (x, y))
        
