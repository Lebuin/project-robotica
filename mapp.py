#!/usr/bin/env python3

from PIL import Image, ImageDraw
import random
import math


class Map:
    
    walls = []
    
    def __init__(self, width, height, resolution):
        '''
        Initialize the map.
        Inputs:
            width: The width of the map in meters.
            height: The height of the map in meters.
            resolution: The size of a pixel in meters.
        '''
        
        self.width = width
        self.height = height
        self.resolution = resolution
        
        self.wpix = int(math.ceil(width / resolution)) + 1
        self.hpix = int(math.ceil(height / resolution)) + 1
        self.floor = [255 for i in range(self.wpix * self.hpix)]
    
    
    def get_pixel(self, coor):
        '''
        Get the value of a pixel on the floor.
        Inputs:
            coor: A tuple (x, y).
        Output:
            An integer in the range [0,255].
        '''
        
        return self.floor[self.wpix*coor[1] + coor[0]]
    
    
    def set_pixel(self, coor, value):
        '''
        Set a pixel on the floor.
        Inputs:
            coor: A tuple (x, y).
            value: An integer in the range [0,255].
        '''
        
        self.floor[self.wpix*coor[1] + coor[0]] = value
    
    
    def is_empty(self, coor):
        '''
        Check if a pixel has been coloured.
        Inputs:
            coor: A tuple (x, y).
        Output:
            True if the pixel is empty, False otherwise.
        '''
        
        return self.get_pixel(coor) == 255
    
    
    def meter_to_pixel(self, coor):
        '''
        Convert a coordinate in meters to a pixel coordinate.
        Inputs:
            coor: A tuple (x, y).
        Output:
            A tuple (x, y).
        '''
        
        x = int(round(coor[0] / self.resolution))
        y = self.hpix - int(round(coor[1]/self.resolution)) - 1
        return (x, y)
    
    
    
    def get_coordinate(self, coor):
        '''
        Get the colour of a coordinate in meters.
        Inputs:
            coor: A tuple (x, y)
        Output:
            The value of the colour at the given location.
        '''
        
        return self.get_pixel(meter_to_pixel(coor))
    
    
    def fill_floor(self, num_areas, num_colours):
        '''
        Draw the colours on the floor of the map.
        Inputs:
            num_areas: The number of differently colored areas.
            num_colours: The number of different colours allowed.
        '''
        
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
                if x+i >= 0 and x+i < self.wpix and \
                    y+j >= 0 and y+j < self.hpix and \
                    self.is_empty((coor[0]+i, coor[1]+j)):
                        todo.append((coor, colour))
    
    
    def place_walls(self, num):
        '''
        Put walls on the map.
        Inputs:
            num: The number of walls to place.
        '''
        
        # Add walls around the map.
        self.walls.extend([
            ((0, 0), (self.width, 0)),
            ((self.width, 0), (self.width, self.height)),
            ((self.width, self.height), (0, self.height)),
            ((0, self.height), (0, 0))
        ])
        
        # Put num extra walls on the map.
        for i in range(num):
            
            # Calculate a random begin point for the wall.
            x_start = random.random() * self.width
            y_start = random.random() * self.height
            
            # Calculate an end point, making sure it is in the map.
            size = (self.width + self.height) / 2
            length = random.gauss(size / 2, size / 4)
            angle = random.random() * 2*math.pi
            x_end = min(
                self.width,
                max(0, x_start + length * math.cos(angle))
            )
            y_end = min(
                self.height,
                max(0, y_start + length * math.sin(angle))
            )
            
            # Add the wall to the list of walls.
            self.walls.append(((x_start, y_start), (x_end, y_end)))
    
    
    def draw_map(self, path):
        '''
        Draw the map to an image file.
        Inputs:
            path: The path to the file, including an extension accepted
                by PIL.
        '''
        
        im = Image.new('L', (self.wpix, self.hpix))
        
        # Draw the floor.
        im.putdata(self.floor)
        
        # Draw the walls as lines.
        draw = ImageDraw.Draw(im)
        for wall in self.walls:
            w = (
                self.meter_to_pixel(wall[0]),
                self.meter_to_pixel(wall[1])
            )
            draw.line(w, fill=0)
        
        im.save(path)
