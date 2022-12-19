from laser_offset.geometry_2d.bounds2d import Bounds2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.vector2d import Vector2d

from typing import List, Sequence

from laser_offset.geometry_2d.size2d import Size2d
from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style

from laser_offset.geometry_2d.normalize_angle import normalize_angle

import math

class Arc2d(Shape2d):
    style: Style

    start: Point2d
    end: Point2d
    
    radiuses: Size2d
    angle: float

    large_arc: bool
    sweep_flat: bool
    
    @classmethod
    def fromCenteredArc(cls,
                        style: Style,
                        center: Point2d,
                        start_angle: float,
                        end_angle: float,
                        radius: float
                       ) -> 'Arc2d':
        
        start_point: Point2d = center + Vector2d.polar(radius, start_angle)
        end_point: Point2d = center + Vector2d.polar(radius, end_angle)
        
        # print("ARC ANGLES: ", math.degrees(end_angle), math.degrees(start_angle),math.degrees(end_angle) - math.degrees(start_angle))
        
        large_arc: bool = (end_angle < start_angle) ^ (abs(start_angle - end_angle) > math.pi)
        
        return Arc2d(Style(),
                     start_point,
                     end_point,
                     Size2d(radius, radius),
                     normalize_angle(end_angle - start_angle),
                     large_arc,
                     True)

    def __init__(self,
        style: Style,

        start: Point2d,
        end: Point2d,
    
        radiuses: Size2d,
        angle: float,

        large_arc: bool,
        sweep_flat: bool
    
    ) -> None:
        super().__init__(style)
        self.start = start
        self.end = end
        self.radiuses = radiuses
        self.angle = angle
        self.large_arc = large_arc
        self.sweep_flat = sweep_flat


    @property
    def isClosed(self) -> bool:
        return False

    @property
    def center(self) -> Point2d:
        raise RuntimeError("Not Implemented")

    @property
    def bounds(self) -> Bounds2d:
        raise RuntimeError("Not Implemented")
        
    @property
    def inverse(self) -> 'Shape2d':
        invertedArc = Arc2d(self.style, self.end, self.start, self.radiuses, self.angle, self.large_arc, not self.sweep_flat)
        return invertedArc