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
        self.alp_fast = 0.5
        self.w_slow = 0.1
        self.w_fast = 0.1
        self.w_random = 0
        
        self.alp_dist = 0.3
        self.w_dist = 10
        
        self.num_particles = num_particles
        self.particles = []
        
        self.mapp = mapp
        
        # Draw num_particles random particles inside the map.
        for i in range(self.num_particles):
            self.particles.append((self.random_particle(), 0))
    
    def random_particle(self):
        close = True
        while close:
            x = random.random() * self.mapp.width
            y = random.random() * self.mapp.height
            close = self.mapp.closest_wall((x, y)) < self.size
        ang = random.random() * 2*math.pi
        return (ang, (x, y))
    
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
        
        while ang > 2*math.pi:
            ang -= 2*math.pi
        while ang < -2*math.pi:
            ang += 2*math.pi
        
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
        Output:
            True if the particles approximate the robot pose good
            enough.
        """
        
        u = (ang, dist)
        
        # Move the robot.
        _, new_state = self.motion_model(u, exact=exact)
        self.ang, self.coor = new_state
        self.measurement = self.measure()
        
        # Initialize the temporary particle list with a dummy particle.
        # Elements are of the form ((ang, (x, y)), weight)
        temp = [((0, (0, 0)), 0)]
        for particle in self.particles:
            _, new_part = self.motion_model(u, particle[0])
            weight = self.measurement_model(new_part, particle[1])
            
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
            if random.random() < self.w_random:
                rand_particles.append((self.random_particle(), 0))
            else:
                selector = random.random() * total_weight
                
                # Find the largest temporary particle whose cumulative
                # weight is smaller than the random selector.
                k = 0
                while temp[k][1] < selector:
                    k += 1
                self.particles.append((temp[k][0], temp[k][2]))
        
        # See if the non-random particles are close enough yet.
        self.w_dist += self.alp_dist * (self.particles_distance() - self.w_dist)
        self.particles.extend(rand_particles)
        
        return self.w_dist < 0.5
    
    def particles_distance(self):
        """
        Calculate the average distance of the best portion of the
        particles to the actual robot position.
        """
        
        avg_num = len(self.particles)//3
        distances = []
        distances = [geom.dist_points(self.coor, p[0][1]) for p in self.particles]
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
            particles=[p[0] for p in self.particles]
        )


class Robot1(Robot):
    
    half_measures = 25  # Half of the number of measurements (the total
                        # number must be even to simplify calculations.)
    min_range = -10   # The minimal and
    max_range = 10  # maximal measuring distance.
    hit_sigma = 0.3 # See Thrun p. 172.
    
    #measurement = []
    
    def __init(self, mapp, num_particles):
        self.measurement = []
        super(Robot, self).__init__(mapp, num_particles)
    
    def set_weights(self, particles):
        """
        Update the moving averages used to determine the number of
        random particles that will be drawn.
        Inputs:
            particles: A list with the temporary particles:
                (coordinate, cumulative weight, weight).
        """
        
        w_max = max([p[2]**(1/len(self.measurement)) for p in particles])
        
        self.w_slow += self.alp_slow * (w_max - self.w_slow)
        self.w_fast += self.alp_fast * (w_max - self.w_fast)
        self.w_random = 1 - 2*self.w_fast
    
    def measure(self, state=None, exact=False):
        """
        Do a range scan around a location on the map.
        Inputs:
            state: A tuple of the form (angle, (x, y)) describing the
                robot location.
            exact: A boolean describing wether or not to incorporate
                noise in the measurements.
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
        
        measurement = []
        
        # Do range_resolution measurements angles with uniform
        # differences.
        for i in range(self.half_measures):
            theta = math.pi * i / self.half_measures
            if exact:
                real_angle = ang + theta
            else:
                real_angle = random.gauss(ang + theta, self.a_sigma)
            beam = (
                coor, (
                    coor[0] + math.cos(real_angle),
                    coor[1] + math.sin(real_angle)
                )
            )
            
            # Loop through all the walls, and see if the beam hits them.
            # Do this in both positive and negative direction, so that
            # at the end of the loop we have the distances to the
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
            if not exact:
                pos_dist += random.gauss(0, self.d_sigma * pos_dist)
                neg_dist += random.gauss(0, self.d_sigma * neg_dist)
            
            measurement.append((
                theta,
                min(self.max_range, pos_dist)
            ))
            measurement.append((
                theta - math.pi,
                min(self.max_range, -neg_dist)
            ))
        
        return measurement
    
    def measurement_model(self, particle, old_weight):
        """
        Calculate the probability of a measurement at a location of the
        robot.
        Inputs:
            particle: A tuple (angle, (x, y)).
            old_weight: the old weight of the particle.
        Output:
            The probability of the measurement.
        """
        
        ang, coor = particle
        new_weight = 1
        sqrt2pi = math.sqrt(2*math.pi)  # Repeatedly used constant
        
        # Calculate the probability of each measurement and multiply
        # them in prob.
        for meas in self.measurement:
            if meas[1] != self.max_range:
                x = coor[0] + meas[1] * math.cos(ang + meas[0])
                y = coor[1] + meas[1] * math.sin(ang + meas[0])
                d = self.mapp.closest_wall((x, y))
                
                # Multiply the total measurement probability by the 
                # probability of this measurement, using a Gauss function
                # with mean 0 and std dev hit_sigma.
                w = math.exp(-d**2 / (2*self.hit_sigma**2)) / (self.hit_sigma*sqrt2pi) + 0.01
                
                new_weight *= w
        
        return new_weight
    
    def autonome_move(self):
        """
        Find out an optimal direction to move in, and perform the move.
        Output:
            True if the particles approximate the robot pose good
            enough.
        """
        
        # Only use the 10% of the particles with the highest weight.
        particles = sorted(self.particles, key=lambda p: p[1], reverse=True)
        particles = [p[0] for p in particles[:5]]
        
        measurements = []
        for p in particles:
            state = (0, p[1])
            measurements.append(self.measure(state=state, exact=True))
        
        # Create a root state with empty angles list and usability
        # factor 0. States always contain
        #   - A list with angles in which to rotate and move in order
        #     to reach the state.
        #   - The usability factor of the state.
        #   - A list of particles that must be used to find the best
        #     directions. Particles are of the form (angle, (x, y)).
        states = [([], 0, particles)]
        depth = 5
        
        # Go depth steps deep to find the best direction under which to
        # move the robot.
        for i in range(depth):
            # Only preserve the 3 best states to speed up calculations.
            states = states[:2]
            new_states = []
            
            # Calculate all the children states for the preserved
            # states and add them to a new list of states. Sort the list
            # based on the usability factor.
            for state in states:
                new_states.extend(self.new_states(state, measurements))
            states = sorted(new_states, key=lambda s: s[1], reverse=True)
        
        # Take the best angle (the one with the highest factor) from the
        # list and perform the actual move.
        angle = states[0][0][0]
        return self.move(angle, 1)
    
    def new_states(self, state, measurements):
        """
        This function is used by self.autonome_move(). Given a set of
        particles, determine what the best directions are in order to
        find the robot pose.
        Inputs:
            state: A tuple describing the state. See 
                self.autonome_move() for a full explanation.
            measurements: A list with the measurements of the root
                particles from self.autonome_move().
        Output:
            A list of new state similar to the input.
        """
        
        angles = [i/5 * math.pi for i in range(-2, 3)]
        fav = {}
        particles = state[2]
        new_states = []
        
        # Loop through the list of angles that must be examined.
        for angle in angles:
            u = (angle, 1)
            new_particles = []
            
            # Calculate the next pose for all particles. Measure at the
            # new pose and calculate the difference of this measurement
            # with the measurement of the corresponding root particle.
            # A higher difference is better.
            factor = 0
            for i in range(len(particles)):
                _, new_part = self.motion_model(u, particles[i], exact=True)
                new_particles.append(new_part)
                new_state = (0, new_part[1])
                measurement = self.measure(state=new_state, exact=True)
                
                avg_diff = 0
                for m in range(2*self.half_measures):
                    meas = measurements[i][m][1]
                    avg_diff += abs(meas - measurement[m][1])
                avg_diff /= 2*self.half_measures
                factor += avg_diff / len(particles)
            
            # Add a state to the list of new states.
            new_states.append((
                state[0]+[angle],
                state[1]+factor,
                new_particles
            ))
        
        return new_states


class Robot2(Robot):
    
    measurement = 0
    
    def set_weights(self, particles):
        """
        Update the moving averages used to determine the number of
        random particles that will be drawn.
        Inputs:
            particles: A list with the temporary particles: 
                (coordinate, cumulative weight, weight).
        """
        
        w_avg = sum([p[2] for p in particles]) / self.num_particles
        
        self.w_slow += self.alp_slow * (w_avg - self.w_slow)
        self.w_fast += self.alp_fast * (w_avg - self.w_fast)
        self.w_random = 1 - 4*self.w_fast
    
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
        
        return self.mapp.get_coordinate(coor)
    
    def measurement_model(self, particle, old_weight):
        """
        Calculate the probability of a measurement at a location of the
        robot.
        Inputs:
            particle: A tuple (angle, (x, y)).
            old_weight: the old weight of the particle.
        Output:
            The probability of the measurement.
        """
        
        if self.mapp.get_coordinate(particle[1]) == self.measurement:
            new_weight = 1
        else:
            new_weight = 0
        
        return 0.1*old_weight + 0.9*new_weight
    
    def autonome_move(self):
        """
        Find out an optimal direction to move in, and perform the move.
        Output:
            True if the particles approximate the robot pose good
            enough.
        """
        
        # Only use the 20% of the particles with the highest weight.
        particles = sorted(self.particles, key=lambda p: p[1], reverse=True)
        particles = [p[0] for p in particles[:self.num_particles//5]]
        
        # Create a root state with empty angles list and usability
        # factor 0. States always contain
        #   - A list with previously found angles.
        #   - The usability factor of the state.
        #   - A list of particles that must be used to find the best
        #     directions. Particles are of the form (angle, (x, y)).
        states = [([], 0, particles)]
        depth = 4
        
        # Go depth steps deep to find the best direction under which to
        # move the robot.
        for i in range(depth):
            # Only preserve the 3 best states to speed up calculations.
            states = states[:3]
            new_states = []
            
            # Calculate all the children states for the preserved
            # states and add them to a new list of states. Sort the list
            # based on the usability factor.
            for state in states:
                new_states.extend(self.new_states(state))
            states = sorted(new_states, key=lambda s: s[1])
        
        # Take the best angle (the one with the highest factor) from the
        # list and perform the actual move.
        angle = states[0][0][0]
        return self.move(angle, 1)
    
    def new_states(self, state):
        """
        This function is used by self.autonome_move(). Given a set of
        particles, determine what the best directions are in order to
        find the robot pose.
        Inputs:
            state: A tuple describing the state. See 
                self.autonome_move() for a full explanation.
        Output:
            A list of new state similar to the input.
        """
        
        angles = [
            0,
            math.pi/6, -math.pi/6,
            math.pi/3, -math.pi/3,
            3*math.pi/4, -3*math.pi/4
        ]
        angles = [i/5 * math.pi for i in range(-2, 3)]
        fav = {}
        particles = state[2]
        new_states = []
        
        # Loop through the list of angles that must be examined.
        for angle in angles:
            u = (angle, 1)
            new_particles = []
            
            # Calculate the next pose for all particles, and measure at
            # the same time.
            count = {}
            for p in particles:
                _, new_part = self.motion_model(u, p, exact=True)
                new_particles.append(new_part)
                meas = self.measure(state=new_part)
                if not meas in count:
                    count[meas] = 1
                else:
                    count[meas] += 1
            
            # Calculate the usability factor. This is the sum of the
            # squares of the frequencies of the floor colours measured
            # by the different particles. Lower is better.
            factor = sum([c**2 for c in count.values()])
            
            # Add a state to the list of new states.
            new_states.append((
                state[0]+[angle],
                state[1]+factor,
                new_particles
            ))
        
        return new_states
