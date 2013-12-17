#!/usr/bin/env python3

from PIL import Image
import random

class Map:
    
    def __init__(self, width, height):
        '''
        Initialize the map.
        Inputs:
            width: The width of the map in pixels.
            height: The height of the map in pixels.
        '''
        
        self.width = width
        self.height = height
        self.floor = [255 for i in range(width*height)]
    
    
    def get_pixel(self, x, y):
        '''
        Get a pixel on the floor.
        Inputs:
            x: The x-coordinate of the pixel.
            y: The y-coordinate of the pixel.
        Output:
            An integer in the range [0,255].
        '''
        
        return self.floor[self.width*y + x]
    
    
    def set_pixel(self, x, y, value):
        '''
        Set a pixel on the floor.
        Inputs:
            x: The x-coordinate of the pixel.
            y: The y-coordinate of the pixel.
            value: An integer in the range [0,255].
        '''
        
        self.floor[self.width*y + x] = value
    
    
    def is_empty(self, x, y):
        '''
        Check if a pixel has been coloured.
        Inputs:
            x: The x-coordinate of the pixel.
            y: The y-coordinate of the pixel.
        Output:
            True if the pixel is empty, False otherwise.
        '''
        
        return self.get_pixel(x, y) == 255
    
    
    def fill_floor(self, num_areas, num_colours):
        '''
        Draw the colours on the floor of the map.
        Inputs:
            num_areas: The number of differently colored areas.
            num_colours: The number of different colours allowed.
        '''
        
        # Calculate the boundaries and distances between the different
        # possible colours.
        min_colour = 100
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
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            todo.append((x, y, colours[i]))
        
        # Keep going untill the entire floor is painted.
        while len(todo):
            
            # Get a random pixel from the todo list.
            x, y, colour = todo.pop(random.randint(0, len(todo)-1))
            
            # Put this pixel on the floor if it is empty.
            if self.is_empty(x, y):
                self.set_pixel(x, y, colour)
            
            # Add empty neighbouring pixels to the todo list. Give them
            # the same colour as the current pixel.
            for i,j in [(-1,0), (1,0), (0,-1), (0,1)]:
                if x+i >= 0 and x+i < self.width and \
                    y+j >= 0 and y+j < self.height and \
                    self.is_empty(x+i, y+j):
                        todo.append((x+i, y+j, colour))
    
        
    def place_obstacles(self, num):
        '''
        Put obstacles on the map.
        Inputs:
            num: The number of obstacles to place.
        '''
    
        
        pass
    
    
    def draw_map(self, path):
        '''
        Draw the map to an image file.
        Inputs:
            path: The path to the file, including an extension accepted
                by PIL.
        '''
        
        im = Image.new('L', (self.width, self.height))
        im.putdata(self.floor)
        im.save(path)
