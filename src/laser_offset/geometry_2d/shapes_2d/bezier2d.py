from laser_offset.geometry_2d.bounds2d import Bounds2d
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style


class Bezier2d(Shape2d):

    style: Style

    start: Point2d
    end: Point2d
    startControl: Point2d
    endControl: Point2d

    def __init__(self,
        style: Style,
        start: Point2d,
        end: Point2d,
        startControl: Point2d,
        endControl: Point2d
        ) -> None:
            super().__init__(style)
            self.start = start
            self.end = end
            self.startControl = startControl
            self.endControl = endControl

    @property
    def isClosed(self) -> bool:
        return False

    @property
    def center(self) -> Point2d:
        raise RuntimeError("Not Implemented")

    @property
    def bounds(self) -> Bounds2d:
        raise RuntimeError("Not Implemented")
