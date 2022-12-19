from laser_offset.geometry_2d.point2d import Point2d
import math

from laser_offset.geometry_2d.vector2d import Vector2d
from typing import List, Optional

class Segment2d:

    start: Point2d
    end: Point2d

    def __init__(self, start: Point2d, end: Point2d) -> None:
        self.start = start
        self.end = end

    @property
    def length(self) -> float:
        return math.sqrt((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2)

    def is_point_on_segment(self, point: Point2d) -> bool:
        start_dist = self.start.distance(point)
        end_dist = self.end.distance(point)
        seglen = self.length
        
        if start_dist <= seglen and end_dist <= seglen:
            return True
        
        return False

    def intersection(self, another) -> List[Point2d]:

        from laser_offset.geometry_2d.arc_segment_2d import ArcSegment2d
        
        if isinstance(another, Segment2d):

            return self.intersction_segment(another)

        elif isinstance(another, ArcSegment2d):

            return self.intersction_arc_segment(another)

        else:
            return []

    def intersction_segment(self, another: 'Segment2d') -> List[Point2d]:

        x1,y1 = self.start.as_cartesian_tuple
        x2,y2 = self.end.as_cartesian_tuple
        x3,y3 = another.start.as_cartesian_tuple
        x4,y4 = another.end.as_cartesian_tuple

        denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
#         print('denom', denom)
        if denom == 0: # parallel
            return []
        
        ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
#         print('ua', ua)
        if ua < 0 or ua > 1: # out of range
            return []
        
        ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
#         print('ub', ub)        
        if ub < 0 or ub > 1: # out of range
            return []
        
        x = x1 + ua * (x2-x1)
        y = y1 + ua * (y2-y1)
        
        return [Point2d.cartesian(x, y)]

    def intersction_arc_segment(self, another: 'ArcSegment2d') -> List[Point2d]:

        return another.intersection(self)