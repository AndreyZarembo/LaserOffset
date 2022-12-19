from laser_offset.geometry_2d.bounds2d import Bounds2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.point2d import Point2d

from typing import List, Sequence

from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style


class Polyline2d(Shape2d):

    style: Style
    points: List[Point2d]

    def __init__(self, style: Style, points: List[Point2d]) -> None:
        super().__init__(style)
        self.points = points

    @property
    def vertexes(self) -> Sequence[Point2d]:
        return self.points

    @property
    def isClosed(self) -> bool:
        raise RuntimeError("Not Implemented")

    @property
    def center(self) -> Point2d:
        raise RuntimeError("Not Implemented")

    @property
    def bounds(self) -> Bounds2d:
        raise RuntimeError("Not Implemented")
