from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.bounds2d import Bounds2d
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.size2d import Size2d

from typing import Sequence

from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style

from laser_offset.geometry_2d.bounds_rect_2d import BoundsRect2d

class Circle2d(Shape2d):

    style: Style

    centerPoint: Point2d
    radius: float

    def __init__(self, style: Style, centerPoint: Point2d, radius: float) -> None:
        super().__init__(style)
        self.radius = radius        
        self.centerPoint = centerPoint    

    @property
    def isClosed(self) -> bool:
        return True

    @property
    def center(self) -> Point2d:
        return self.centerPoint

    @property
    def bounds(self) -> Bounds2d:
        return Bounds2d(Size2d(self.radius, self.radius))

    @property
    def maxBoundary(self) -> BoundsRect2d:
        return BoundsRect2d(self.center.x - self.radius,
                            self.center.y - self.radius,
                            self.center.x + self.radius,
                            self.center.y + self.radius)