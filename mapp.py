#!/usr/bin/env python3

from PIL import Image, ImageDraw
import random
import math
import shelve

import geom

class Map:
    
    wall_spacing = 0.8
    
    def __init__(self, width, height, resolution):
        """
        Initialize the map.
        Inputs:
            width: The width of the map in meters.
            height: The height of the map in meters.
            resolution: The size of a pixel in meters.
        """
        
        self.walls = []
        
        self.width = width
        self.height = height
        self.resolution = resolution
        
        self.wpix = int(math.ceil(width / resolution)) + 1
        self.hpix = int(math.ceil(height / resolution)) + 1
        self.floor = [255 for i in range(self.wpix * self.hpix)]
    
    def get_pixel(self, coor):
        """
        Get the value of a pixel on the floor.
        Inputs:
            coor: A tuple (x, y).
        Output:
            An integer in the range [0,255].
        """
        
        return self.floor[self.wpix*coor[1] + coor[0]]
    
    def set_pixel(self, coor, value):
        """
        Set a pixel on the floor.
        Inputs:
            coor: A tuple (x, y).
            value: An integer in the range [0,255].
        """
        
        self.floor[self.wpix*coor[1] + coor[0]] = value
    
    def is_empty(self, coor):
        """
        Check if a pixel has been coloured.
        Inputs:
            coor: A tuple (x, y).
        Output:
            True if the pixel is empty, False otherwise.
        """
        
        return self.get_pixel(coor) == 255
    
    def coor_to_pixel(self, coor):
        """
        Convert a coordinate in meters to a pixel coordinate.
        Inputs:
            coor: A tuple (x, y).
        Output:
            A tuple (x, y).
        """
        
        x = int(round(coor[0]/self.resolution))
        y = self.hpix - int(round(coor[1]/self.resolution)) - 1
        return (x, y)
    
    def get_coordinate(self, coor):
        """
        Get the colour of a coordinate in meters.
        Inputs:
            coor: A tuple (x, y)
        Output:
            The value of the colour at the given location.
        """
        
        return self.get_pixel(self.coor_to_pixel(coor))
    
    def closest_wall(self, coor):
        """
        Calculate the distance to the closest wall in meters.
        Inputs:
            coor: A tuple (x, y).
        Output:
            The distance to the closest wall.
        """
        
        min_d = float('inf')
        for wall in self.walls:
            d = geom.dist_point_line(coor, wall)
            if d < min_d:
                min_d = d
        
        return min_d
    
    def intersect_wall(self, line):
        """
        Check if the given line intersects with any of the walls.
        Inputs:
            line: A tuple ((x_start, y_start), (x_end, y_end))
        Output:
            True if the line intersects at least one wall.
        """
        
        for wall in self.walls:
            if geom.dist_line_line(line, wall) == 0:
                return True
        
        return False
    
    def fill_floor(self, num_areas, num_colours):
        """
        Draw the colours on the floor of the map.
        Inputs:
            num_areas: The number of differently colored areas.
            num_colours: The number of different colours allowed.
        """
        
        # Calculate the boundaries and distances between the different
        # possible colours.
        min_colour = 120
        max_colour = 200
        mult = (max_colour - min_colour) / (num_colours-1)
        
        # Randomly choose the colours the seeds will have.
        colours = [random.randint(0, num_colours-1) for i in range(num_areas)]
        colours = list(map(lambda c: int(c*mult) + min_colour, colours))
        
        # Make a todo-list which will contain the location and colour
        # of the pixels that are allowed to be filled at that moment.
        # Fill this list with the random locations of the seeds.
        todo = []
        for i in range(num_areas):
            x = random.randint(0, self.wpix-1)
            y = random.randint(0, self.hpix-1)
            todo.append(((x, y), colours[i]))
        
        # Keep going untill the entire floor is painted.
        while len(todo):
            
            # Get a random pixel from the todo list.
            coor, colour = todo.pop(random.randint(0, len(todo)-1))
            
            # Put this pixel on the floor if it is empty.
            if self.is_empty(coor):
                self.set_pixel(coor, colour)
            
            # Add empty neighbouring pixels to the todo list. Give them
            # the same colour as the current pixel.
            for i,j in [(-1,0), (1,0), (0,-1), (0,1)]:
                x, y = coor[0] + i, coor[1] + j
                if(x >= 0 and x < self.wpix and
                        y >= 0 and y < self.hpix and
                        self.is_empty((x, y))):
                    todo.append(((x, y), colour))
    
    def place_walls(self, num, length):
        """
        Put walls on the map.
        Inputs:
            num: The number of walls to place.
            length: The average length of the walls.
        """
        
        # Add walls around the map.
        self.walls.extend([
            ((0, 0), (self.width, 0)),
            ((self.width, 0), (self.width, self.height)),
            ((self.width, self.height), (0, self.height)),
            ((0, self.height), (0, 0))
        ])
        
        # Put num extra walls on the map.
        for i in range(num):
            
            # Find a start point and angle for the wall so that it can
            # be at least 1 meter long, while maintaining 1 meter
            # distance to all other walls.
            close = True
            while close:
                x_start = random.random() * self.width
                y_start = random.random() * self.height
                ang = random.random() * 2*math.pi
                
                x_end = x_start + math.cos(ang)
                y_end = y_start + math.sin(ang)
                
                close = (
                    self.closest_wall((x_start, y_start)) < 1 or
                    self.closest_wall((x_end, y_end)) < 1
                )
            
            # Make the wall as long as possible without coming closer
            # than 1 meter to any other wall.
            step = 9
            close = False
            while not close:
                step += 1
                x_end = x_start + 0.1*step * math.cos(ang)
                y_end = y_start + 0.1*step * math.sin(ang)
                close = (
                    self.closest_wall((x_end, y_end)) < 1.1 or
                    random.random() < 0.1 / length
                )
            
            # Add the found wall to the list of walls.
            self.walls.append(((x_start, y_start), (x_end, y_end)))
        
    
    def draw(self, floor=True, walls=True, robot=None, particles=None):
        """
        Draw the map to an image.
        Inputs:
            floor: A boolean that sets whether the floor will be drawn.
            walls: Id. for the walls.
            robot: A tuple (x, y) that gives the robot location.
            particles: A list with (x, y)-tuples that give the locations
                of the particles that must be drawn.
        """
        
        im = Image.new('RGB', (self.wpix, self.hpix))
        draw = ImageDraw.Draw(im)
        
        # Draw the floor.
        if floor:
            data = [(a, a, a) for a in self.floor]
            im.putdata(data)
        
        # Draw the robot as a red 2x2 square.
        if robot is not None:
            x, y = robot
            x1 = int(math.floor(x/self.resolution))
            y1 = self.hpix - int(math.floor(y/self.resolution)) - 1
            x2 = int(math.ceil(x/self.resolution))
            y2 = self.hpix - int(math.ceil(y/self.resolution)) - 1
            draw.rectangle((x1, y1, x2, y2), fill=(255, 0, 0))
        
        # Draw the walls as lines.
        if walls:
            for wall in self.walls:
                w = (
                    self.coor_to_pixel(wall[0]),
                    self.coor_to_pixel(wall[1])
                )
                draw.line(w, fill=0)
        
        # Draw the particles as green/yellow points.
        if particles is not None:
            pixels = {}
            max_value = 0
            
            for particle in particles:
                p = self.coor_to_pixel(particle[1])
                if p not in pixels:
                    pixels[p] = 0
                pixels[p] += 1
                
                if pixels[p] > max_value:
                    max_value = pixels[p]
            
            for p in pixels:
                value = int(255 * pixels[p] / max_value)
                particle = (value, 255, 255-value)
                base = im.getpixel(p)
                
                colour = tuple([int(0.4*x + 0.6*y) for x,y in zip(base, particle)])
                im.putpixel(p, colour)
        
        return im
    
    def save(self, path):
        """
        Save the floor and walls layout to a file that can be read by
        self.load().
        Inputs:
            path: The filename.
        """
        
        db = shelve.open(path, 'c')
        db['floor'] = self.floor
        db['walls'] = self.walls
        db.close()
    
    def load(self, path):
        """
        Load the floor and walls layout from a file that was created by
        self.save().
        Inputs:
            path: The filename.
        """
        
        db = shelve.open(path, 'r')
        self.floor = db['floor']
        self.walls = db['walls']
        db.close()
