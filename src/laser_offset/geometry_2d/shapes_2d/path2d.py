from abc import ABC
from operator import le
from laser_offset.geometry_2d.bounds2d import Bounds2d
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.line2d import Line2d
from laser_offset.geometry_2d.shapes_2d.arc2d import Arc2d

from typing import List, NamedTuple
from laser_offset.geometry_2d.size2d import Size2d

from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style
from laser_offset.geometry_2d.vector2d import Vector2d

import math

class PathComponent(ABC):
    pass



class Path2d(Shape2d):
    """Path Shape
    """

    style: Style

    components: List[PathComponent]

    def __init__(self, style: Style, components: List[PathComponent]) -> None:
        super().__init__(style)
        self.components = components
        
    @classmethod
    def pathFromShapes(self, chain: List[Shape2d]) -> 'Path2d':
        components = list()
        components.append(MoveOrigin(chain[0].start))
        for shape in chain:
            if isinstance(shape, Line2d):
                components.append(Line(shape.end))

            elif isinstance(shape, Arc2d):
                # components.append(      Arc(shape.end, shape.radiuses, shape.angle, shape.large_arc, shape.sweep_flat))
                components.append(SimpleArc(shape.end, shape.radiuses.width, not shape.sweep_flat, shape.large_arc))            

        components.append(ClosePath())
        return Path2d(Style(), components)        
        

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
    def relative(self) -> 'Shape2d':
        relative_components: List[PathComponent] = list()
        current_point: Point2d = None
        for index, component in enumerate(self.components):
            if current_point is None:
                relative_components.append(component)
            
            else:
                
                if isinstance(component, MoveOrigin):
                    relative = Vector2d.cartesian(component.target.x - current_point.x, component.target.y - current_point.y)
                    relative_components.append(RelMoveOrigin(relative))
                elif isinstance(component, Line):
                    relative = Vector2d.cartesian(component.target.x - current_point.x, component.target.y - current_point.y)
                    relative_components.append(RelLine(relative))
                elif isinstance(component, Arc):
                    relative = Vector2d.cartesian(component.target.x - current_point.x, component.target.y - current_point.y)
                    relative_components.append(RelArc(relative, component.radiuses, component.angle, component.large_arc, component.sweep))
                elif isinstance(component, SimpleArc):
                    relative = Vector2d.cartesian(component.target.x - current_point.x, component.target.y - current_point.y)
                    relative_components.append(RelSimpleArc(relative, component.radius, component.cw_direction, component.large_arc))
                elif isinstance(component, ClosePath):
                    relative_components.append(ClosePath())

            if isinstance(component, MoveOrigin):
                current_point = component.target
            elif isinstance(component, Line):
                current_point = component.target
            elif isinstance(component, Arc):
                current_point = component.target
            elif isinstance(component, SimpleArc):
                current_point = component.target

        return Path2d(self.style, relative_components)


class MoveOrigin(PathComponent):

    target: Point2d
    def __init__(self, target: Point2d) -> None:
        super().__init__()
        self.target = target

class RelMoveOrigin(PathComponent):

    target: Vector2d
    def __init__(self, target: Vector2d) -> None:
        super().__init__()
        self.target = target



class Line(PathComponent):

    target: Point2d
    def __init__(self, target: Point2d) -> None:
        super().__init__()
        self.target = target

class RelLine(PathComponent):

    target: Vector2d
    def __init__(self, target: Vector2d) -> None:
        super().__init__()
        self.target = target



class HorizontalLine(PathComponent):

    length: float
    def __init__(self, length: float) -> None:
        super().__init__()
        self.length = length

class RelHorizontalLine(PathComponent):

    length: float
    def __init__(self, length: float) -> None:
        super().__init__()
        self.length = length



class VerticalLine(PathComponent):

    length: float
    def __init__(self, length: float) -> None:
        super().__init__()
        self.length = length

class RelVerticalLine(PathComponent):

    length: float
    def __init__(self, length: float) -> None:
        super().__init__()
        self.length = length



class ClosePath(PathComponent):

    def __init__(self) -> None:
        super().__init__()



class CubicBezier(PathComponent):

    target: Point2d
    startControlPoint: Point2d
    endControlPoint: Point2d
    def __init__(self,
        target: Point2d,
        startControlPoint: Point2d,
        endControlPoint: Point2d
    ) -> None:
        super().__init__()
        self.target = target
        self.startControlPoint = startControlPoint
        self.endControlPoint = endControlPoint

class RelCubicBezier(PathComponent):

    target: Vector2d
    startControlPoint: Vector2d
    endControlPoint: Vector2d
    def __init__(self,
        target: Vector2d,
        startControlPoint: Vector2d,
        endControlPoint: Vector2d
    ) -> None:
        super().__init__()
        self.target = target
        self.startControlPoint = startControlPoint
        self.endControlPoint = endControlPoint



class StrugBezier(PathComponent):

    target: Point2d
    endControlPoint: Point2d
    def __init__(self,
        target: Point2d,
        endControlPoint: Point2d
    ) -> None:
        super().__init__()
        self.target = target
        self.endControlPoint = endControlPoint

class RelStrugBezier(PathComponent):

    target: Vector2d
    endControlPoint: Vector2d
    def __init__(self,
        target: Vector2d,
        endControlPoint: Vector2d
    ) -> None:
        super().__init__()
        self.target = target
        self.endControlPoint = endControlPoint



class Quadratic(PathComponent):

    target: Point2d
    controlPoint: Point2d
    def __init__(self, target: Point2d, controlPoint: Point2d) -> None:
        super().__init__()
        self.target = target
        self.controlPoint = controlPoint

class RelQuadratic(PathComponent):

    target: Vector2d
    controlPoint: Vector2d
    def __init__(self, target: Vector2d, controlPoint: Vector2d) -> None:
        super().__init__()
        self.target = target
        self.controlPoint = controlPoint



class ReflectedQuadratic(PathComponent):

    target: Point2d
    def __init__(self, target: Point2d) -> None:
        super().__init__()
        self.target = target

class RelReflectedQuadratic(PathComponent):

    target: Vector2d
    def __init__(self, target: Vector2d) -> None:
        super().__init__()
        self.target = target        

class SimpleArc(PathComponent):
    target: Point2d
    radius: float
    cw_direction: bool
    large_arc: bool
    def __init__(self,
        target: Point2d,
        radius: float,
        cw_direction: bool,
        large_arc: bool
    ) -> None:
        super().__init__()
        self.target = target
        self.radius = radius
        self.cw_direction = cw_direction
        self.large_arc = large_arc

class RelSimpleArc(PathComponent):
    target: Vector2d
    radius: float
    cw_direction: bool
    large_arc: bool
    def __init__(self,
        target: Vector2d,
        radius: float,
        cw_direction: bool,
        large_arc: bool
    ) -> None:
        super().__init__()
        self.target = target
        self.radius = radius
        self.cw_direction = cw_direction
        self.large_arc = large_arc


class Arc(PathComponent):

    target: Point2d
    radiuses: Size2d
    angle: float
    large_arc: bool
    sweep: bool
    def __init__(self,
        target: Point2d,
        radiuses: Size2d,
        angle: float,
        large_arc: bool,
        sweep: bool
    ) -> None:
        super().__init__()
        self.target = target
        self.radiuses = radiuses
        self.angle = angle
        self.large_arc = large_arc
        self.sweep = sweep

class RelArc(PathComponent):

    target: Vector2d
    radiuses: Size2d
    angle: float
    large_arc: bool
    sweep: bool
    def __init__(self,
        target: Vector2d,
        radiuses: Size2d,
        angle: float,
        large_arc: bool,
        sweep: bool
    ) -> None:
        super().__init__()
        self.target = target
        self.radiuses = radiuses
        self.angle = angle
        self.large_arc = large_arc
        self.sweep = sweep

    
class ArcInfo(NamedTuple):
    center: Point2d
    startAngle: float
    endAngle: float
    deltaAngle: float
    cw: bool
    startVector: Vector2d
    endVector: Vector2d
    radius: float

    def __str__(self) -> str:
        return "ArcInfo\n\tcenter:\t{center}\n\tstart angle:\t{sa}\n\tend angle:\t{ea}\n\tclockwise:\t{cw}\n\tradius:\t{r}".format(
            center=self.center,
            sa=self.startAngle,
            ea=self.endAngle,
            cw=self.cw,
            r=self.radius
        )

# conversion_from_endpoint_to_center_parameterization
# sample :  svgArcToCenterParam(200,200,50,50,0,1,1,300,200)
# x1 y1 rx ry φ fA fS x2 y2
def arc_info(prev_point: Point2d, arc: SimpleArc) -> ArcInfo:

    def radian(ux: float, uy: float, vx: float, vy: float):
        dot: float = ux * vx + uy * vy
        mod: float = math.sqrt( ( ux * ux + uy * uy ) * ( vx * vx + vy * vy ) )
        rad: float = math.acos( dot / mod )
        if ux * vy - uy * vx < 0.0:
            rad = -rad
    
        return rad

    x1: float = prev_point.x
    y1: float = prev_point.y
    rx: float = arc.radius
    ry: float = arc.radius
    phi: float = 0
    fA: float = arc.large_arc
    fS: float = arc.cw_direction
    x2: float = arc.target.x
    y2: float = arc.target.y

    PIx2: float = math.pi * 2.0
#var cx, cy, startAngle, deltaAngle, endAngle;
    if rx < 0:
        rx = -rx

    if ry < 0:
        ry = -ry

    if rx == 0.0 or ry == 0.0:
        raise RuntimeError('Raidus can not be zero')

    
    s_phi: float = math.sin(phi)
    c_phi: float = math.cos(phi)
    hd_x: float = (x1 - x2) / 2.0 # half diff of x
    hd_y: float = (y1 - y2) / 2.0 # half diff of y
    hs_x: float = (x1 + x2) / 2.0 # half sum of x
    hs_y: float = (y1 + y2) / 2.0 # half sum of y

    # F6.5.1
    x1_: float = c_phi * hd_x + s_phi * hd_y
    y1_: float = c_phi * hd_y - s_phi * hd_x

    # F.6.6 Correction of out-of-range radii
    # Step 3: Ensure radii are large enough
    lambda_: float = (x1_ * x1_) / (rx * rx) + (y1_ * y1_) / (ry * ry)
    if lambda_ > 1:
        rx = rx * math.sqrt(lambda_)
        ry = ry * math.sqrt(lambda_)
    
    rxry: float = rx * ry
    rxy1_: float = rx * y1_
    ryx1_: float = ry * x1_

    sum_of_sq: float = rxy1_ * rxy1_ + ryx1_ * ryx1_ # sum of square
    if sum_of_sq == 0:
        raise RuntimeError('start point can not be same as end point ', prev_point.__str__(), arc.radius)
    
    coe: float = math.sqrt(abs((rxry * rxry - sum_of_sq) / sum_of_sq))
    if fA == fS:
        coe = -coe

    # F6.5.2
    cx_: float = coe * rxy1_ / ry
    cy_: float = -coe * ryx1_ / rx

    # F6.5.3
    cx = c_phi * cx_ - s_phi * cy_ + hs_x
    cy = s_phi * cx_ + c_phi * cy_ + hs_y

    xcr1: float = (x1_ - cx_) / rx
    xcr2: float = (x1_ + cx_) / rx
    ycr1: float = (y1_ - cy_) / ry
    ycr2: float = (y1_ + cy_) / ry

    # F6.5.5
    startAngle: float = radian(1.0, 0.0, xcr1, ycr1)

    # F6.5.6
    deltaAngle = radian(xcr1, ycr1, -xcr2, -ycr2)
    while deltaAngle > PIx2:
        deltaAngle -= PIx2

    while deltaAngle < 0.0:
        deltaAngle += PIx2

    if fS == False or fS == 0:
        deltaAngle -= PIx2

    endAngle = startAngle + deltaAngle
    while endAngle > PIx2:
        endAngle -= PIx2
    while endAngle < 0.0: 
        endAngle += PIx2

    rotationSign: float = 1 if fS else -1

    startVector: Vector2d = Vector2d.polar(1, startAngle + rotationSign * math.pi/2)
    endVector: Vector2d = Vector2d.polar(1, endAngle + rotationSign * math.pi/2)

    outputObj: ArcInfo = ArcInfo(
        Point2d.cartesian(cx, cy),
        startAngle,
        endAngle,
        deltaAngle,
        fS == True or fS == 1,
        startVector,
        endVector,
        arc.radius
        )
    
    return outputObj
