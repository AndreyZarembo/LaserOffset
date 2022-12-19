from abc import ABC
from importlib.machinery import FrozenImporter
from math import fabs
from operator import ne
from turtle import st
from typing import List, Sequence

from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.bounds2d import Bounds2d
from laser_offset.geometry_2d.bounds2d import Size2d
from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.fill_style import FillStyle
from laser_offset.geometry_2d.style2d import Style


class Shape2d(ABC):

    vertexes: Sequence[Point2d]
    style: Style

    def __init__(self, style: Style) -> None:
        super().__init__()
        self.style = style
    
    @property
    def isClosed(self) -> bool:
        return False

    @property
    def center(self) -> Point2d:
        return Point2d.origin

    @property
    def bounds(self) -> Bounds2d:
        return Bounds2d(Size2d(0,0))
        
    @property
    def relative(self) -> 'Shape2d':
        return self

    @property
    def inverse(self) -> 'Shape2d':
        return self
