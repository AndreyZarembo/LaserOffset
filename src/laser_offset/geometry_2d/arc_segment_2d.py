from laser_offset.geometry_2d.angle_range import AngleRange
from laser_offset.geometry_2d.point2d import Point2d
import math

from laser_offset.geometry_2d.vector2d import Vector2d
from typing import List, Optional

from laser_offset.geometry_2d.normalize_angle import normalize_angle
from laser_offset.math.float_functions import fclose
from laser_offset.geometry_2d.shapes_2d.path2d import Arc
from laser_offset.geometry_2d.arc_info import ArcInfo

class ArcSegment2d:

    center: Point2d
    radius: float
    
    start_angle: float
    end_angle: float

    start: Point2d
    end: Point2d

    clockwise: bool

    def __init__(self, center: Point2d, radius: float, start_angle: float, end_angle: float, clockwise: bool) -> None:
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.start = self.center + Vector2d.polar(radius, self.start_angle)
        self.end = self.center + Vector2d.polar(radius, self.end_angle)
        self.clockwise = clockwise
        
    @classmethod
    def fromArc(cls, prev_point: Point2d, arc: Arc) -> 'ArcSegment2d':
        arcinfo = ArcInfo.fromArc(prev_point, arc.target, arc.radius, arc.large_arc, arc.cw_direction)
        return ArcSegment2d(arcinfo.center, arc.radius, arcinfo.startAngle, arcinfo.endAngle, arcinfo.cw)

    @property
    def delta_angle(self) -> float:
        return normalize_angle(self.end_angle - self.start_angle)
    
    @property
    def length(self) -> float:
        return self.radius * self.delta_angle

    def is_point_in_segment(self, point: 'Point2d') -> bool:
            cp = Vector2d.fromTwoPoints(self.center, point)

            rng: AngleRange = AngleRange(self.start_angle, self.end_angle, self.clockwise)
            return rng.has_angle(cp.da)
    
    def intersection(self, another) -> List[Point2d]:

        from laser_offset.geometry_2d.segment_2d import Segment2d

        if isinstance(another, Segment2d):
            return self.intersction_segment(another)

        elif isinstance(another, ArcSegment2d):
            return self.intersction_arc_segment(another)

        else:
            return []

    def intersction_segment(self, another: 'Segment2d') -> List[Point2d]:
        
        def is_point_on_arc_and_segment(point: Point2d) -> bool:
            return self.is_point_in_segment(point) and another.is_point_on_segment(point)
        
        cO = self.center
        r = self.radius
        sA = another.start
        sB = another.end
        
        As = sA.y - sB.y
        Bs = sB.x - sA.x
        Cs = sA.x * sB.y - sB.x * sA.y
        
        d = abs(As*cO.x + Bs*cO.y + Cs) / math.sqrt(As ** 2 + Bs ** 2)
                
        if d > r:
            return []
        
        Ap = -Bs
        Bp = As
        Cp = Bs * cO.x - As * cO.y
        
        A1 = Ap
        B1 = Bp
        C1 = Cp
        
        A2 = As
        B2 = Bs
        C2 = Cs
        
        H = Point2d.cartesian(
            - (C1 * B2 - C2 * B1) / (A1 * B2 - A2 * B1),
            - (A1 * C2 - A2 * C1) / (A1 * B2 - A2 * B1)
        )
        
        if abs(d - r) <= 1e-5 and is_point_on_arc_and_segment(H):
            # Проверить, что H попадает на арку и отрезок
            return [H]
        else:
            # Две точки
            
            l = math.sqrt( r ** 2 - d ** 2)
            vA = Vector2d.fromTwoPoints(sB, sA)
            vB = Vector2d.fromTwoPoints(sA, sB)
            
            p1 = H + vA.single_vector * l
            p2 = H + vB.single_vector * l

            # print(H)
            # print(p1)
            # print(p2)
            # print(vA)
            # print(vA.single_vector)
            # print(vB)
            # print(vB.single_vector)
            # print(l)
            # return [H, sA, sB, p1, p2]
            
            result = list()
            if is_point_on_arc_and_segment(p1):
                result.append(p1)
            if is_point_on_arc_and_segment(p2):
                result.append(p2)
            
            return result
        
        return []

    def intersction_arc_segment(self, another: 'ArcSegment2d') -> List[Point2d]:

        arc_a = self
        arc_b = another
        
        r0 = arc_a.radius
        r1 = arc_b.radius
        
        A = arc_a.center
        B = arc_b.center
        AB = A.distance(B)
        
        d = AB

        if d > r0 + r1:
            return []
        elif (d < abs(r0 - r1)) or abs(d) <= 1e-5:
            return []

        a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)

        if abs(d - (r0 + r1)) <= 1e-5 or fclose(abs(r0), abs(a)):

            H = Point2d.cartesian(
                A.x + a*(B.x - A.x)/d,
                A.y + a*(B.y - A.y)/d,
            )


            if arc_a.is_point_in_segment(H) and arc_b.is_point_in_segment(H):
                return [H]
            else:
                return []
        else:

            # print(r0, r1, a)
            h = math.sqrt(r0 ** 2 - a ** 2)

            H = Point2d.cartesian(
                A.x + a*(B.x - A.x)/d,
                A.y + a*(B.y - A.y)/d,
            )

            point1_x = H.x + h * (B.y - A.y) / d
            point1_y = H.y - h * (B.x - A.x) / d
            point1 = Point2d.cartesian(point1_x, point1_y)
            
            point2_x = H.x - h * (B.y - A.y) / d
            point2_y = H.y + h * (B.x - A.x) / d
            point2 = Point2d.cartesian(point2_x, point2_y)
            
            result = list()
            
            if arc_a.is_point_in_segment(point1) and arc_b.is_point_in_segment(point1):
                result.append(point1)

            if arc_a.is_point_in_segment(point2) and arc_b.is_point_in_segment(point2):
                result.append(point2)
                
            return result
        
        return []