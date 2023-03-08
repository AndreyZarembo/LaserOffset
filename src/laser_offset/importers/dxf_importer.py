from enum import Enum
from re import X
from sys import path_hooks
from turtle import width
from typing import List, NamedTuple, Optional, Tuple, cast
from codecs import StreamReader

from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.circle2d import Circle2d
from laser_offset.geometry_2d.shapes_2d.line2d import Line2d
from laser_offset.geometry_2d.shapes_2d.arc2d import Arc2d
from laser_offset.geometry_2d.shapes_2d.path2d import Arc, ClosePath, Line, MoveOrigin, Path2d, PathComponent, SimpleArc
from laser_offset.geometry_2d.size2d import Size2d
from laser_offset.geometry_2d.style2d import Style
from laser_offset.importers.importer import Importer

from laser_offset.geometry_2d.canvas2d import Canvas2d

from laser_offset.math.float_functions import fclose, fzero

import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from ezdxf.layouts.layout import Paperspace
from ezdxf.entities import DXFEntity
from ezdxf.entities.lwpolyline import LWPolyline

import math

class DXFPathPoint(NamedTuple):
    x: float
    y: float
    ws: float
    we: float
    bulge: float

    @classmethod
    def fromTuple(cls, point: Tuple[float, float, float, float, float]) -> 'DXFPathPoint':
        return DXFPathPoint(point[0], point[1], point[2], point[3], point[4])


class PointType(Enum):
    FIRST = 0
    MIDDLE = 1
    LAST = 2

class DXFImporter(Importer):

    def import_canvas(self, relative: bool, reader: StreamReader) -> Canvas2d:
        
        doc: Drawing = ezdxf.read(reader)
        
        model_space: Modelspace = doc.modelspace()

        paper_space: Paperspace = doc.layouts.active_layout()
        min_x = paper_space.dxf.limmin[0]
        min_y = paper_space.dxf.limmin[1]
        max_x = paper_space.dxf.limmax[0]
        max_y = paper_space.dxf.limmax[1]
        width = max_x - min_x
        height = max_y - min_y


        shapes: List[Shape2d] = list()
        
        for child in model_space:
            entity: DXFEntity = child
            
            if entity.dxftype() == 'CIRCLE':
                circle: Circle2d = self.read_circle(entity)
                shapes.append(circle)
                
            elif entity.dxftype() == 'LWPOLYLINE':
                path: Path2d = self.read_path2d(entity)
                shapes.append(path)
                
            elif entity.dxftype() == 'LINE':
                line: Line2d = self.read_line2d(entity)
                shapes.append(line)                
                
            elif entity.dxftype() == 'ARC':
                arc: Arc2d = self.read_arc2d(entity)
                shapes.append(arc)

            elif entity.dxftype() == 'SPLINE':
                spline_as_path: Path2d = self.read_spline_as_path2d(entity)
                shapes.append(spline_as_path)
                
            else:
                print('UNKNOWN TYPE: ',entity.dxftype())

        canvas: Canvas2d = Canvas2d(
            Point2d.cartesian(0, 0), 
            Size2d(width, height), shapes)

        if relative:
            return canvas.relative

        return canvas

    def read_line2d(self, entity: ezdxf.entities.line.Line) -> Line2d:
        return Line2d(Style(), 
                      Point2d.cartesian(entity.dxf.start.x, entity.dxf.start.y), 
                      Point2d.cartesian(entity.dxf.end.x, entity.dxf.end.y))
    
    def read_arc2d(self, entity: ezdxf.entities.arc.Arc) -> Arc2d:
        return Arc2d.fromCenteredArc(Style(),
                                     Point2d.cartesian(entity.dxf.center.x, entity.dxf.center.y),
                                     math.radians(entity.dxf.start_angle),
                                     math.radians(entity.dxf.end_angle),
                                     entity.dxf.radius
                                    )
                     

    def read_circle(self, entity: DXFEntity) -> Circle2d:
        cx: float = entity.dxf.center.x
        cy: float = entity.dxf.center.y
        r: float = entity.dxf.radius
        return Circle2d(Style(), Point2d.cartesian(cx, cy), r)

    def read_path2d(self, entity: LWPolyline) -> Path2d:
        
        components: List[PathComponent] = list()
        points: List[Tuple[float, float, float, float, float]] = self.flip_y(entity)

        for index, point in enumerate(points+[points[0]]):

            point_type: PointType = PointType.MIDDLE
            if index == 0:
                point_type = PointType.FIRST


            prev_point = points[index - 1] if index > 0 else points[entity.__len__()-1]
            start_point: DXFPathPoint = DXFPathPoint.fromTuple(prev_point)
            end_point: DXFPathPoint = DXFPathPoint.fromTuple(point)
            component: PathComponent = self.read_path_component(point_type, start_point, end_point)
            if component is not None:
                components.append(component)

            if index == points.__len__() - 1:
                point_type = PointType.LAST
                component: PathComponent = self.read_path_component(point_type, start_point, end_point)
                if component is not None:
                    components.append(component)

        if entity.closed:
            start_point: Point2d = cast(MoveOrigin, components[0]).target
            end_point: Point2d
            if isinstance(components[-1], SimpleArc):
                end_point = components[-1].target
            elif isinstance(components[-1], Line):
                end_point = components[-1].target

            if not fclose(start_point.x, end_point.x) or not fclose(start_point.y, end_point.y):
                components.append(Line(start_point))

            components.append(ClosePath())

        return Path2d(Style(), components)

    def read_path_component(self, point_type: PointType, start: DXFPathPoint, end: DXFPathPoint) -> Optional[PathComponent]:
        if point_type == PointType.FIRST:
            return self.read_move(start, end)

        elif point_type == PointType.LAST:
            return self.read_close_path(start, end)

        if start.bulge == 0:
            return self.read_line(start, end)

        else:
            return self.read_arc(start, end)

    def read_move(self, start: DXFPathPoint, end: DXFPathPoint) -> Optional[MoveOrigin]:
        return MoveOrigin(Point2d.cartesian(end.x, end.y))

    def read_line(self, start: DXFPathPoint, end: DXFPathPoint) -> Optional[Line]:
        return Line(Point2d.cartesian(end.x, end.y))

    def read_arc(self, start: DXFPathPoint, end: DXFPathPoint) -> Optional[Arc]:

        dx: float = end.x - start.x
        dy: float = end.y - start.y
        l: float = math.sqrt( dx ** 2 + dy ** 2)
        k: float = l / 2
        b: float = abs(start.bulge)

        r: float = k * (b ** 2 + 1) / (2 * b)

        cw_direction: bool = start.bulge < 0
        large_arc: bool = abs(b) > 1.0

        return SimpleArc(Point2d.cartesian(end.x, end.y), r, cw_direction, large_arc)

    def read_close_path(self, start: DXFPathPoint, end: DXFPathPoint) -> Optional[ClosePath]:
        if start.x == end.x and start.y == end.y:
            return ClosePath()
        else:
            return None

    def flip_y(self, input_points: List[Tuple[float, float, float, float, float]]) -> List[Tuple[float, float, float, float, float]]:
        polyline_points: List[Tuple[float, float, float, float, float]] = list()
        for point in input_points:
            polyline_points.append((point[0], point[1], point[2], point[3], point[4]))
        return polyline_points

    def read_spline_as_path2d(self, entity: ezdxf.entities.spline.Spline ) -> Path2d:

        components: List[PathComponent] = list()

        step_point = entity.control_points[0]

        prev_point = Point2d.cartesian(step_point[0], step_point[1])
        components.append(MoveOrigin(prev_point))

        for step_point in entity.flattening(0.05, 3):
            point = Point2d.cartesian(step_point.x, step_point.y)
            if not fzero(prev_point.distance(point)):
                components.append(Line(point))
            prev_point = point

        # step_point = entity.control_points[-1]
        # components.append(Line(Point2d.cartesian(step_point[0], step_point[1])))

        if entity.closed:
            components.append(ClosePath())

        return Path2d(Style(), components)