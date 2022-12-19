from abc import ABC
from cmath import nan, sqrt
import math
from typing import Optional, Tuple

from laser_offset.geometry_2d.vector2d import CartesianVector2d, PolarVector2d, Vector2d

from laser_offset.math.float_functions import fzero

class Point2d(ABC):

    x: float
    y: float

    r: float
    a: float

    @classmethod
    def origin(cls) -> 'Point2d':
        return OriginPoint()

    @classmethod
    def cartesian(cls, x: float, y: float) -> 'Point2d':
        return CartesianPoint2d(x, y)

    @classmethod
    def polar(cls, r: float, a: float) -> 'Point2d':
        return PolarPoint2d(r, a)
    
    def eq(self, another: 'Point2d') -> float:
        return fzero(self.distance(another))

    def distance(self, another: 'Point2d') -> float:
        return math.sqrt((another.x - self.x) ** 2 + (another.y - self.y) ** 2)

    def __add__(self, another):
        if not isinstance(another, Vector2d):
            raise RuntimeError("Point2d cat only + with Vector2d")

    def __str__(self) -> str:
        return "{x:.3f},{y:.3f}/{r:.3f}@{a:.3f}".format(
            x=self.x,
            y=self.y,
            r=self.r,
            a=self.a
        )

    def equals(self, another: 'Point2d') -> bool:
        if  abs(self.x - another.x) <= 1e-5 and abs(self.y - another.y) <= 1e-5:
            return True

        return False

    @property
    def as_cartesian_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @property
    def as_polar_tuple(self) -> Tuple[float, float]:
        return (self.r, self.a)

class OriginPoint(Point2d):

    x: float
    y: float

    r: float
    a: float

    def __init__(self) -> None:
        super().__init__()
        self.x = 0
        self.y = 0
        self.r = 0
        self.a = 0

    def __str__(self) -> str:
        return "0,0"

    def __add__(self, another):
        if isinstance(another, CartesianVector2d):
            return CartesianPoint2d(another.dx, another.dy)
        if isinstance(another, PolarVector2d):
            return PolarPoint2d(another.dr, another.da)
        return super.__add__(another)


class CartesianPoint2d(Point2d):

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        self.x = x
        self.y = y

    @property
    def r(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def a(self) -> float:
        return math.atan2(self.y, self.x)

    def __add__(self, another):
        if isinstance(another, Vector2d):
            return CartesianPoint2d(self.x + another.dx, self.y + another.dy)
        return super.__add__(another)


class PolarPoint2d(Point2d):

    r: float
    a: float

    def __init__(self, r: float, a: float) -> None:
        super().__init__()
        self.r = r
        self.a = a

    @property
    def x(self) -> float:
        return self.r * math.cos(self.a)
    
    @property
    def y(self) -> float:
        return self.r * math.sin(self.a)

    def __add__(self, another):
        if isinstance(another, Vector2d):
            return PolarPoint2d(self.r + another.dr, self.a + another.da)
        return super.__add__(another)
