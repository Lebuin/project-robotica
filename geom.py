#!/usr/bin/env python3

import math

def dist_line_line(l1, l2):
    """
    Calculate the distance between two line segments.
    Inputs:
        l1: A tuple with the begin and end points of the line segment:
            ((x1, y1), (x2, y2))
        l2: Id.
    Output:
        The distance between the line segments.
    """
    t1, t2 = intersect_lines(l1, l2)
    if t1 >= 0 and t1 <= 1 and t2 >= 0 and t2 <= 1:
        return 0
    else:
        return min(
            dist_point_line(l1[0], l2),
            dist_point_line(l1[1], l2),
            dist_point_line(l2[0], l1),
            dist_point_line(l2[1], l1)
        )

def dist_point_line(p0, l):
    """
    Calculate the distance between a point and a line segment.
    Inputs:
        p0: A tuple with the coordinates of the point: (x, y).
        l: A tuple with the begin and end points of the line segment:
            ((x1, y1), (x2, y2))
    Output:
        The distance between the point and the line segment.
    """
    
    p1 = l[0]
    p2 = l[1]
    
    # Calculate t so that the projection of p0 on the line is at the
    # point p1 + t*(p2-p1): t = dot(p0-p1, p2-p1) / |p1, p2|**2
    dot = ((p0[0]-p1[0])*(p2[0]-p1[0]) +  (p0[1]-p1[1])*(p2[1]-p1[1]))
    sqnorm = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
    t = dot / sqnorm
    
    # If t is negatif, p1 is the closest point of the line segment.
    if t < 0:
        return dist_points(p0, p1)
    
    # If t > 1, p2 is the closest point.
    elif t > 1:
        return dist_points(p0, p2)
    
    # Otherwise, the orthogonal projection is the closest point.
    else:
        projection = (
            p1[0] + t * (p2[0]-p1[0]),
            p1[1] + t * (p2[1]-p1[1])
        )
        return dist_points(p0, projection)

def dist_points(a, b):
    """
    Calculate the distance between two points.
    Inputs:
        a: A tuple (x, y).
        b: Id.
    Output:
        The distance between the two points.
    """
    
    return math.hypot(b[0]-a[0], b[1]-a[1])

def intersect_lines(l1, l2):
    '''
    Get the parameters for which the two lines intersect. If these both 
    lie between 0 and 1, the lines intersect between their begin and end
    point.
    Inputs:
        l1: A tuple of the form ((x_start, y_start), (x_end, y_end)).
        l2: Id.
    Output:
        A tuple containing the parameters for the two lines: (p1, p2).
    '''
    
    a1, a2 = l1[0], l1[1]
    b1, b2 = l2[0], l2[1]
    
    t1 = ((b1[1]-b2[1]) * (a1[0]-b1[0]) - (b1[0]-b2[0]) * (a1[1]-b1[1]))
    t2 = ((a1[1]-a2[1]) * (a1[0]-b1[0]) - (a1[0]-a2[0]) * (a1[1]-b1[1]))
    n = ((b2[0]-b1[0]) * (a1[1]-a2[1]) - (a1[0]-a2[0]) * (b2[1]-b1[1]))
    
    if n == 0: # The lines are parallel
        return (float('inf'), float('inf'))
    else:
        return (t1/n, t2/n)
