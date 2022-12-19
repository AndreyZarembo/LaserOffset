from abc import ABC
from cmath import sqrt
import math
from xmlrpc.client import Boolean
from laser_offset.geometry_2d.normalize_angle import normalize_angle
# from vectors.geometry_2d.point2d import Point2d

class Vector2d(ABC):

    dx: float
    dy: float

    dr: float
    da: float

    @classmethod
    def fromTwoPoints(cls, start: 'Point2d', end: 'Point2d') -> 'Vector2d':
        return Vector2d.cartesian(end.x - start.x, end.y - start.y)

    @classmethod
    def origin(cls) -> 'Vector2d':
        return ZeroVector()

    @classmethod
    def cartesian(cls, dx: float, dy: float) -> 'Vector2d':
        return CartesianVector2d(dx, dy)

    @classmethod
    def polar(cls, dr: float, da: float) -> 'Vector2d':
        return PolarVector2d(dr, normalize_angle(da))

    def __str__(self) -> str:
        return "->{dx:.3f},{dy:.3f}/{dr:.3f}@{da:.3f}".format(
            dx=self.dx,
            dy=self.dy,
            dr=self.dr,
            da=self.da
        )

    @property
    def norm(self) -> float:
        return math.sqrt( self.dx ** 2 + self.dy ** 2)

    @property
    def single_vector(self) -> float:
        return Vector2d.polar(1, normalize_angle(self.da))

    @property
    def inv_vector(self) -> float:
        return Vector2d.polar(1, normalize_angle(math.pi + self.da))        

    def __mul__(self, another):
        if isinstance(another, float):
            return Vector2d.polar(self.dr * another, normalize_angle(self.da))
        elif isinstance(another, int):
            return Vector2d.polar(self.dr * another, normalize_angle(self.da))
        
        raise RuntimeError('Invalid Arg')

    @property
    def inverted(self) -> 'Vector2d':
        if isinstance(self, ZeroVector):
            return self
        elif isinstance(self, CartesianVector2d):
            return Vector2d.cartesian(-self.dx, -self.dy)
        elif isinstance(self, PolarVector2d):
            return Vector2d.polar(self.dr, normalize_angle(self.da + math.pi))


    def __add__(self, another):
        if isinstance(another, Vector2d):
            v2: Vector2d = another
            return Vector2d.cartesian(self.dx + v2.dx, self.dy + v2.dy)

        raise RuntimeError('Invalid Arg')
        
class ZeroVector(Vector2d):

    dx: float
    dy: float

    dr: float
    da: float

    def __init__(self) -> None:
        super().__init__()
        self.dx = 0
        self.dy = 0
        self.dr = 0
        self.da = 0

    def __str__(self) -> str:
        return "->0,0"

    @property
    def norm(self) -> float:
        return 0


class CartesianVector2d(Vector2d):

    dx: float
    dy: float

    def __init__(self, dx: float, dy: float) -> None:
        super().__init__()
        self.dx = dx
        self.dy = dy

    @property
    def dr(self) -> float:
        return math.sqrt(self.dx ** 2 + self.dy ** 2)

    @property
    def da(self) -> float:
        return normalize_angle(math.atan2(self.dy, self.dx))


class PolarVector2d(Vector2d):

    dr: float
    da: float

    def __init__(self, dr: float, da: float) -> None:
        super().__init__()
        self.dr = dr
        self.da = normalize_angle(da)

    @property
    def dx(self) -> float:
        return self.dr * math.cos(self.da)
    
    @property
    def dy(self) -> float:
        return self.dr * math.sin(self.da)

    @property
    def norm(self) -> float:
        return self.dr
