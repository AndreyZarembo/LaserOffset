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

from laser_offset.geometry_2d.bounds_rect_2d import BoundsRect2d

from laser_offset.geometry_2d.arc_info import ArcInfo

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
    def maxBoundary(self) -> BoundsRect2d:
        minX = 10000
        minY = 10000
        maxX = -10000
        maxY = -10000
        prev_point = self.start
        for component in self.components:
            if isinstance(component, MoveOrigin):
                move: MoveOrigin = component
                minX = min(minX, move.target.x)
                minY = min(minY, move.target.y)
                maxX = max(maxX, move.target.x)
                maxY = max(maxY, move.target.y)
                prev_point = move.target
            elif isinstance(component, Line):
                line: Line = component
                minX = min(minX, line.target.x)
                minY = min(minY, line.target.y)
                maxX = max(maxX, line.target.x)
                maxY = max(maxY, line.target.y)
                prev_point = line.target
            elif isinstance(component, SimpleArc):
                arc: SimpleArc = component
                arc_info = ArcInfo.fromArc(prev_point,
                                           arc.target,
                                           arc.radius,
                                           arc.large_arc,
                                           arc.cw_direction
                                           )
                minX = min(minX, arc_info.center.x - arc_info.radius)
                minY = min(minY, arc_info.center.y - arc_info.radius)
                maxX = max(maxX, arc_info.center.x + arc_info.radius)
                maxY = max(maxY, arc_info.center.y + arc_info.radius)
                prev_point = arc.target

        return BoundsRect2d(minX, minY, maxX, maxY)

    @property
    def start(self) -> Point2d:
        return self.componentPoint(0)

    @property
    def end(self) -> Point2d:
        if self.components.__len__() == 1:
            return self.start
        last_component = self.components[-1]
        if isinstance(last_component, ClosePath):
            return self.componentPoint(-2)
        else:
            return self.componentPoint(-1)

    def componentPoint(self, component_index: int) -> Point2d:
        component = self.components[component_index]
        if isinstance(component, MoveOrigin):
            move_origin: MoveOrigin = component
            return move_origin.target
        elif isinstance(component, Line):
            line: Line = component
            return line.target
        elif isinstance(component, SimpleArc):
            arc: SimpleArc = component
            return arc.target
        elif isinstance(component, Arc):
            arc: Arc = component
            return arc.target
        
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