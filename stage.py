#!/usr/bin/env python3

from PIL import Image

class Map:
    
    def __init__(self, width, height):
        '''
        Initialize the map.
        Inputs:
            width: The width of the map in pixels.
            height: The height of the map in pixels.
        '''
        
        inputs
        self.width = width
        self.height = height
        self.floor = [0 for i in range(width*height)]
    
    
    def get_pixel(self, x, y):
        '''
        Get a pixel on the floor.
        Inputs:
            x: The x-coordinate of the pixel.
            y: The y-coordinate of the pixel.
        Output:
            An integer in the range [0,255].
        '''
        
        return self.floor[width*y + x]
    
    
    def set_pixel(self, x, y, value):
        '''
        Set a pixel on the floor.
        Inputs:
            x: The x-coordinate of the pixel.
            y: The y-coordinate of the pixel.
            value: An integer in the range [0,255].
        '''
        
        self.floor[width*y + x] = value
    
    
    def fill_floor(self, num):
        '''
        Draw the colours on the floor of the map.
        Inputs:
            num: The number of distinctly colored areas.
        '''
        
        pass
    
        
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
            path: The path to the file, including extension.
        '''
        
        im = Image.new('L', (self.width, self.height))
        im.putdata(self.floor)
        im.save(path)
