#!/usr/bin/env python3

from PIL import Image, ImageDraw
import random
import math


class Map:
    
    def __init__(self, width, height, resolution):
        '''
        Initialize the map.
        Inputs:
            width: The width of the map in meters.
            height: The height of the map in meters.
            resolution: The size of a pixel in meters.
        '''
        
        self.resolution = resolution
        self.width = int(math.ceil(width / resolution)) + 1
        self.height = int(math.ceil(height / resolution)) + 1
        self.floor = [255 for i in range(self.width * self.height)]
        self.obstacles = []
    
    
    def get_pixel(self, x, y):
        '''
        Get the value of a pixel on the floor.
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
    
    
    def get_coordinate(self, x_coor, y_coor):
        '''
        Get the colour of a coordinate in meters.
        Inputs:
            x: The x-coordinate in meters.
            y: The y-coordinate in meters.
        Output:
            The value of the colour at the given location.
        '''
        
        x = int(round(x_coor / self.resolution))
        y = self.height - int(round(y_coor / self.resolution)) - 1
        return self.get_pixel(x, y)
    
    
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
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
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
    
        
    """def place_obstacles(self, num):
        '''
        Put obstacles on the map.
        Inputs:
            num: The number of obstacles to place.
        '''
        
        for i in range(num):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            self.obstacles.append((x, y))"""
    
    def place_obstacles(self, num):
        '''
        Put obstacles on the map.
        Inputs:
            num: The number of obstacles to place.
        '''
        
        # Add walls around the map.
        self.obstacles.extend([
            (0, 0, self.width-1, 0),
            (self.width-1, 0, self.width-1, self.height-1),
            (self.width-1, self.height-1, 0, self.height-1),
            (0, self.height-1, 0, 0)
        ])
        
        for i in range(num):
            
            x_start = random.randint(0, self.width-1)
            y_start = random.randint(0, self.height-1)
            
            size = (self.width + self.height) / 2
            length = random.gauss(size / 2, size / 4)
            angle = random.random() * 2*math.pi
            x_end = min(
                self.width-1,
                max(0, x_start + length * math.cos(angle))
            )
            y_end = min(
                self.height-1,
                max(0, y_start + length * math.sin(angle))
            )
            
            
            '''test = False
            
            while not test:
                
                # Calculate random end points for the line.
                length = random.gauss(size / 2, size / 4)
                angle = random.random() * 2*math.pi
                x_end = x_start + length * math.cos(angle)
                y_end = y_start + length * math.sin(angle)
                
                # Check if the end point is inside the map.
                test = (
                    x_end >= 0 and
                    x_end < self.width and
                    y_end >= 0 and
                    y_end < self.height
                )'''
            
            self.obstacles.append((x_start, y_start, x_end, y_end))
    
    
    def draw_map(self, path):
        '''
        Draw the map to an image file.
        Inputs:
            path: The path to the file, including an extension accepted
                by PIL.
        '''
        
        im = Image.new('L', (self.width, self.height))
        
        # Draw the floor.
        im.putdata(self.floor)
        
        # Draw the obstacles as lines.
        draw = ImageDraw.Draw(im)
        for obstacle in self.obstacles:
            '''x, y = obstacle
            for i in range(-1, 2):
                for j in range(-1, 2):
                    im.putpixel((x+i, y+j), 0)'''
            draw.line(obstacle, fill=0)
        
        im.save(path)
