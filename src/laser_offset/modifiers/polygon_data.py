from typing import NamedTuple, List, Tuple

import math

from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.vector2d import Vector2d
from laser_offset.geometry_2d.shapes_2d.path2d import PathComponent, ClosePath, MoveOrigin, SimpleArc, Line
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.path2d import Path2d
from laser_offset.geometry_2d.shapes_2d.circle2d import Circle2d
from laser_offset.geometry_2d.arc_info import ArcInfo
from laser_offset.geometry_2d.normalize_angle import normalize_angle

class ShapeSegment(NamedTuple):
    component: PathComponent
    start_point: Point2d
    end_point: Point2d
    start_vector: Vector2d
    end_vector: Vector2d
    is_arc: bool
    
class Vertex(NamedTuple):
    point: Point2d
    in_component_prev_point: Point2d
    in_component: PathComponent
    out_component: PathComponent
    in_vector: Vector2d
    out_vector: Vector2d
    angle: float
        
        

def vectors_from_component(prev_point: Point2d, component: PathComponent) -> Tuple[Vector2d, Vector2d]:
    
    if isinstance(component, Line):
        lineVector = Vector2d.cartesian(component.target.x - prev_point.x, component.target.y - prev_point.y)
        return (lineVector, lineVector)
    
    elif isinstance(component, SimpleArc):
        
        arcinfo = ArcInfo.fromArc(prev_point, component.target, component.radius, component.large_arc, component.cw_direction)
        return (arcinfo.startVector, arcinfo.endVector)
        
    raise RuntimeError('Not Implemented')
    
def vertex_from_components(in_component: PathComponent, in_prev_point: Point2d, out_component: PathComponent) -> Vertex:
    
    __, in_vector = vectors_from_component(in_prev_point, in_component)
    out_vector, __ = vectors_from_component(in_component.target, out_component)    

    #   Out-вектор к In-вектору.
    
    i_v = in_vector.inverted
    o_v = out_vector
    angle = normalize_angle(i_v.da - o_v.da)
    
    return Vertex(
        in_component.target,
        in_prev_point,
        in_component,
        out_component,
        in_vector.single_vector,
        out_vector.single_vector,
        angle
    )

def segment_from_component(prev_point: Point2d, component: PathComponent) -> ShapeSegment:
    
    start_vector, end_vector = vectors_from_component(prev_point, component)    
    
    return ShapeSegment(
        component,
        prev_point,
        component.target,
        start_vector.single_vector,
        end_vector.single_vector,
        isinstance(component, SimpleArc)
    )        
        
class PolygonData(NamedTuple):
    segments: List[ShapeSegment]
    vertexes: List[Vertex]
    clockwise: bool
    
    @classmethod
    def fromShape(cls, shape: Shape2d) -> 'PolygonData':
                
        if isinstance(shape, Path2d):
            return PolygonData.fromPath2d(shape)
        elif isinstance(shape, Circle2d):
            return PolygonData.fromCircle2d(shape)
        else:
            print("Unknown type ", type(shape))
            return PolygonData([], [], True)
        
    @classmethod
    def fromPath2d(cls, shape: Path2d) -> 'PolygonData':

        result_segments: List[ShapeSegment] = list()
        result_vertexes: List[Vertex] = list()

        lines_and_arcs = list(filter(lambda component: isinstance(component, Line) or isinstance(component, SimpleArc),
                                     shape.components))
        if not lines_and_arcs[-1].target.equals( shape.components[0].target):
            lines_and_arcs.append(Line(shape.components[0].target))

        momentum = 0

        for index, component in enumerate(lines_and_arcs):

            prev_component = lines_and_arcs[index-1]
            prev_component_start_point = lines_and_arcs[index-2].target

            vertex = vertex_from_components(prev_component, prev_component_start_point, component)
            result_vertexes.append(vertex)

            segment = segment_from_component(prev_component.target, component)
            result_segments.append(segment)

            momentum += (segment.end_point.x - segment.start_point.x) * (segment.end_point.y + segment.start_point.y)

        clockwise: bool = momentum > 0

        updated_vertexes: List[Vertex] = list()
        for vertex in result_vertexes:
            updated_vertexes.append(Vertex(
                vertex.point,
                vertex.in_component_prev_point,
                vertex.in_component,
                vertex.out_component,
                vertex.in_vector,
                vertex.out_vector,
                vertex.angle if not clockwise else normalize_angle(2 * math.pi - vertex.angle)
            ))

        return PolygonData(result_segments, updated_vertexes, clockwise)   
        
        
    @classmethod
    def fromCircle2d(cls, shape: Circle2d) -> 'PolygonData':
        replacement_path: Path2d = Path2d(shape.style, [
            MoveOrigin(Point2d.cartesian(shape.centerPoint.x - shape.radius, shape.centerPoint.y)),
            SimpleArc(
                Point2d.cartesian(shape.centerPoint.x + shape.radius, shape.centerPoint.y),
                shape.radius,
                True,
                False
            ),
            SimpleArc(
                Point2d.cartesian(shape.centerPoint.x - shape.radius, shape.centerPoint.y),
                shape.radius,
                True,
                False
            ),
            ClosePath()
        ])
        
        return cls.fromPath2d(replacement_path)        
        