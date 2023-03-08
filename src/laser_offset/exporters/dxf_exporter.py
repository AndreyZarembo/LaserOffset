import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
import math

from abc import ABC
from codecs import StreamWriter
from typing import Dict, List, Tuple
from laser_offset.exporters.exporter import Exporter

from laser_offset.geometry_2d.canvas2d import Canvas2d
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.line2d import Line2d
from laser_offset.geometry_2d.shapes_2d.circle2d import Circle2d
from laser_offset.geometry_2d.shapes_2d.ellipse2d import Ellipse2d
from laser_offset.geometry_2d.shapes_2d.path2d import HorizontalLine, Line, MoveOrigin, Path2d, RelHorizontalLine, RelLine, RelMoveOrigin, RelVerticalLine, SimpleArc, VerticalLine, HorizontalLine, ClosePath, CubicBezier, RelCubicBezier, Quadratic, RelQuadratic, ReflectedQuadratic, RelReflectedQuadratic, Arc, RelArc, StrugBezier, RelStrugBezier
from laser_offset.geometry_2d.shapes_2d.polygon2d import Polygon2d
from laser_offset.geometry_2d.shapes_2d.polyline2d import Polyline2d
from laser_offset.geometry_2d.shapes_2d.rect2d import Rect2d
from laser_offset.math.float_functions import fge

class DXFExporter(Exporter):

    def export_canvas(self, canvas: Canvas2d, match_size: bool, stream: StreamWriter):

        doc: Drawing = ezdxf.new(dxfversion="R2010")
        model_space: Modelspace = doc.modelspace()

        layer_name = "LASERCUT"

        doc.layers.add(layer_name, color=7)
        dxf_layer_attribs = {"layer": layer_name}

        for shape in canvas.shapes:
            self.write_shape(shape, model_space, dxf_layer_attribs)

        doc.write(stream)
        
    def write_shape(self, shape: Shape2d, model_space: Modelspace, dxf_layer_attribs: Dict[str, str]):
        if isinstance(shape, Line2d):
            self.write_line(shape, model_space, dxf_layer_attribs)
        elif isinstance(shape, Circle2d):
            self.write_circle(shape, model_space, dxf_layer_attribs)
        elif isinstance(shape, Ellipse2d):
            self.write_ellipse(shape, model_space, dxf_layer_attribs)
        elif isinstance(shape, Polyline2d):
            self.write_polyline(shape, model_space, dxf_layer_attribs)
        elif isinstance(shape, Polygon2d):
            self.write_polygon(shape, model_space, dxf_layer_attribs)
        elif isinstance(shape, Path2d):
            self.write_path(shape, model_space, dxf_layer_attribs)

    def write_line(self, line: Line2d, model_space: Modelspace, dxf_layer_attribs: Dict[str, str]):
        model_space.add_line((line.start.x, -line.start.y), (line.end.x, line.end.y), dxfattribs=dxf_layer_attribs)
    
    def write_circle(self, circle: Circle2d, model_space: Modelspace, dxf_layer_attribs: Dict[str, str]):
        model_space.add_circle((circle.center.x, -circle.center.y), circle.radius, dxfattribs=dxf_layer_attribs)

    def write_ellipse(self, ellipse: Ellipse2d, model_space: Modelspace, dxf_layer_attribs: Dict[str, str]):
        model_space.add_ellipse((ellipse.center.x, -ellipse.center.y), major_axis=(0, ellipse.radiuses.height, 0), ratio=ellipse.radiuses.width/ellipse.radiuses.height, dxfattribs=dxf_layer_attribs)

    def write_polyline(self, polyline: Polyline2d, model_space: Modelspace, dxf_layer_attribs: Dict[str, str]):
        points = list(map(lambda point: (point.x, -point.y), polyline.points))
        model_space.add_polyline2d(points, close=False, dxfattribs=dxf_layer_attribs)

    def write_polygon(self, polygon: Polygon2d, model_space: Modelspace, dxf_layer_attribs: Dict[str, str]):
        points = list(map(lambda point: (point.x, -point.y), polygon.points))
        model_space.add_polyline2d(points, close=True, dxfattribs=dxf_layer_attribs)

    def write_path(self, path: Path2d, model_space: Modelspace, dxf_layer_attribs: Dict[str, str]):
        
        polyline_points: List[Tuple[float, float, float, float, float]] = list()
        for index, component in enumerate(path.components):

            if isinstance(component, MoveOrigin):
                polyline_points.append(self.lw_polyline_point_from_move(component))
            elif isinstance(component, Line):
                polyline_points.append(self.lw_polyline_point_from_line(component))
            elif isinstance(component, SimpleArc):
                polyline_points.append(self.lw_polyline_point_from_arc(component))
            elif isinstance(component, Arc):
                polyline_points.append(self.lw_polyline_point_from_arc(component))

            
            if index == 0:
                continue

            if isinstance(component, SimpleArc):
                prev_point = polyline_points[index-1]
                bulge = self.lw_poly_bulge_from_arc(component, prev_point)
                polyline_points[index-1] = (prev_point[0], prev_point[1], prev_point[2], prev_point[2], bulge)

        model_space.add_lwpolyline(self.flip_y(polyline_points), dxfattribs=dxf_layer_attribs)

    def flip_y(self, input_points: List[Tuple[float, float, float, float, float]]) -> List[Tuple[float, float, float, float, float]]:
        polyline_points: List[Tuple[float, float, float, float, float]] = list()
        for point in input_points:
            polyline_points.append((point[0], -point[1], point[2], point[3], -point[4]))
        return polyline_points

    def lw_polyline_point_from_move(self, move: MoveOrigin) -> Tuple[float, float, float, float, float]:
        return (move.target.x, move.target.y, 0, 0, 0)

    def lw_polyline_point_from_line(self, line: Line) -> Tuple[float, float, float, float, float]:
        return (line.target.x, line.target.y, 0, 0, 0)

    def lw_polyline_point_from_arc(self, arc: SimpleArc) -> Tuple[float, float, float, float, float]:
        return (arc.target.x, arc.target.y, 0, 0, 0.0)

    def lw_poly_bulge_from_arc(self, arc: SimpleArc, prev_point: Tuple[float, float, float, float, float]) -> float:
        dx: float = prev_point[0] - arc.target.x
        dy: float = prev_point[1] - arc.target.y
        l: float = math.sqrt( dx ** 2 + dy ** 2)
        if not fge(arc.radius, l/2):
            return 0

        if arc.radius < l / 2:
            l = arc.radius * 2
        
        r: float = arc.radius
        sagitta_a: float = r + math.sqrt(r ** 2 - l ** 2 / 4 )
        sagitta_b: float = r - math.sqrt(r ** 2 - l ** 2 / 4 )

        bulge_a = 2 * sagitta_a / l
        bulge_b = 2 * sagitta_b / l

        dir = -1 if arc.cw_direction else 1

        if arc.large_arc:
            return max(bulge_a, bulge_b) * dir
        else:
            return min(bulge_a, bulge_b) * dir

    # def write_rect(self, rect: Rect2d, model_space: GraphicsFactory, dxf_layer_attribs: Dict[str, str]):
        # model_space.add_shape()