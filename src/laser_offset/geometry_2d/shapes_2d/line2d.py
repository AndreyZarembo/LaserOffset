from laser_offset.geometry_2d.bounds2d import Bounds2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.point2d import Point2d

from typing import Sequence

from laser_offset.geometry_2d.size2d import Size2d
from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style
from laser_offset.geometry_2d.bounds_rect_2d import BoundsRect2d

class Line2d(Shape2d):

    style: Style

    start: Point2d
    end: Point2d

    def __init__(self, style: Style, start: Point2d, end: Point2d) -> None:
        super().__init__(style)
        self.start = start
        self.end = end

    @property
    def vertexes(self) -> Sequence[Point2d]:
        return [
            self.start, 
            self.end
            ]

    @property
    def isClosed(self) -> bool:
        return False

    @property
    def center(self) -> Point2d:
        return Point2d.cartesian((self.start.x + self.end.x)/2, (self.start.y + self.end.y)/2)

    @property
    def bounds(self) -> Bounds2d:
        return Bounds2d(Size2d(self.end.x - self.start.x, self.end.y - self.start.y))

    @property
    def maxBoundary(self) -> BoundsRect2d:
        return BoundsRect2d(min(self.start.x, self.end.x),
                            min(self.start.y, self.end.y),
                            max(self.start.x, self.end.x),
                            max(self.start.y, self.end.y))
    
    @property
    def inverse(self) -> 'Shape2d':
        inverseLine = Line2d(self.style, self.end, self.start)
        return inverseLine

class VerticalLine2d(Line2d):

    style: Style

    start: Point2d
    length: float

    def __init__(self, style: Style, start: Point2d, length: float) -> None:
        super().__init__(style, start, Point2d(start.x, start.y + length))
        self.length = length

class HorizontalLine2d(Line2d):

    style: Style

    start: Point2d
    length: float

    def __init__(self, style: Style, start: Point2d, length: float) -> None:
        super().__init__(style, start, Point2d(start.x + length, start.y))
        self.length = length
