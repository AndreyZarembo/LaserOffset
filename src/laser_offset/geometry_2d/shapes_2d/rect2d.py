from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.point2d import Point2d

from typing import Sequence

from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style

class Rect2d(Shape2d):

    style: Style
    
    left_top: Point2d
    right_bottom: Point2d

    corner_radius: float

    def __init__(self, style: Style, left_top: Point2d, right_bottom: Point2d, corner_radius: float = 0) -> None:
        super().__init__(style)
        self.left_top = left_top
        self.right_bottom = right_bottom
        self.corner_radius = corner_radius
        
    @property
    def width(self) ->  Point2d:
        return self.right_bottom.x - self.left_top.x

    @property
    def height(self) -> Point2d:
        return self.right_bottom.y - self.right_bottom.y
    

    