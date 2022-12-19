from abc import ABC
from codecs import StreamWriter
import re
from turtle import st, width
from typing import Dict, List
from laser_offset.exporters.exporter import Exporter
import math

from laser_offset.geometry_2d.canvas2d import Canvas2d
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.line2d import Line2d
from laser_offset.geometry_2d.shapes_2d.circle2d import Circle2d
from laser_offset.geometry_2d.shapes_2d.ellipse2d import Ellipse2d
from laser_offset.geometry_2d.shapes_2d.path2d import HorizontalLine, Line, MoveOrigin, Path2d, RelHorizontalLine, RelLine, RelMoveOrigin, RelSimpleArc, RelVerticalLine, SimpleArc, VerticalLine, HorizontalLine, ClosePath, CubicBezier, RelCubicBezier, Quadratic, RelQuadratic, ReflectedQuadratic, RelReflectedQuadratic, Arc, RelArc, StrugBezier, RelStrugBezier
from laser_offset.geometry_2d.shapes_2d.polygon2d import Polygon2d
from laser_offset.geometry_2d.shapes_2d.polyline2d import Polyline2d
from laser_offset.geometry_2d.shapes_2d.rect2d import Rect2d


class SVGTag:
    tag: str
    attributes: Dict[str, str]
    content: List['SVGTag']

    def __init__(self,
        tag: str,
        attributes: Dict[str, str],
        content: List['SVGTag'] = list()    
    ) -> None:
        self.tag = tag
        self.attributes = attributes
        self.content = content
    
    def merge_attributes(self, attributes: Dict[str, str]) -> 'SVGTag':

        merged_attributes = self.attributes.copy()
        for key, val in attributes.items():
            merged_attributes[key] = val

        return SVGTag(
            self.tag,
            merged_attributes,
            self.content
            )
        

class SVGExporter(Exporter):

    units: str
    scale: float
    skip_xml: bool

    def __init__(self, units: str = "mm", scale: float = 3.7795*0.75, skip_xml: bool = False):
        super().__init__()
        self.units = units
        self.scale = scale
        self.skip_xml = skip_xml

    def export_canvas(self, canvas: Canvas2d, match_size: bool, stream: StreamWriter):

        viewboxWidth = 100
        
        svg_content = """{xml_header}
<svg viewBox="{viewbox_size}" xmlns:svgjs="http://svgjs.com/svgjs" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
    {lines}
</svg>
        """.format(
            xml_header='<?xml version="1.0" encoding="UTF-8"?>' if not self.skip_xml else '',
            viewbox_size=" ".join(map(lambda n: self.convert_number(n), [
                -canvas.size.width/2,
                -canvas.size.height/2,
                canvas.size.width,
                canvas.size.height
            ])),
            width=self.convert_number(canvas.size.width, use_units=True),
            height=self.convert_number(canvas.size.height, use_units=True),
            lines="\n".join(
                map(
                    lambda shape: "\t"+self.export_shape(shape), 
                    canvas.shapes
                    )))

        stream.write(svg_content)

    def export_shape(self, shape: Shape2d) -> str:
        stroke_attributes = self.stroke_attributes(shape)
        shape_tag = self.shape_to_tag(shape)
        result_tag = shape_tag.merge_attributes(stroke_attributes)
        result = self.export_tag(result_tag)
        return result
        

    def stroke_attributes(self, shape: Shape2d) -> Dict[str, str]:
        result: Dict[str, str] = dict()
        result["stroke"] = shape.style.stroke_style.color
        result["stroke-width"] = shape.style.stroke_style.width
        result["fill"] = shape.style.fill_style.color
        return result

    def shape_to_tag(self, shape: Shape2d) -> SVGTag:
        if isinstance(shape, Rect2d):
            return self.rectange_to_tag(shape)
        elif isinstance(shape, Line2d):
            return self.line_to_tag(shape)
        elif isinstance(shape, Circle2d):
            return self.circle_to_tag(shape)
        elif isinstance(shape, Ellipse2d):
            return self.ellipse_to_tag(shape)
        elif isinstance(shape, Polyline2d):
            return self.polyline_to_tag(shape)
        elif isinstance(shape, Polygon2d):
            return self.polygon_to_tag(shape)
        elif isinstance(shape, Path2d):
            return self.path_to_tag(shape)
        else:
            print("Unknown shape type ", type(shape), " ",shape)


    def export_tag(self, tag: SVGTag) -> str:
        attributes_list = list(map(lambda key_val: '{attribute}="{value}"'.format(
            attribute=key_val[0], 
            value=key_val[1]
            ), tag.attributes.items() ))

        if tag.content.__len__() == 0:
            return "<{tag_name} {attributes}/>".format(tag_name=tag.tag, attributes=" ".join(attributes_list))
        else:
            return """
            <{tag_name} {attributes}>
                <!-- TODO CONTENT -->
            </{tag_name}>
            """.format(tag_name=tag.tag, attributes=" ".join(attributes_list))

    def rect_to_tag(self, rect: Rect2d) -> SVGTag:
        return SVGTag(
            "rectangle",
            {
                "x": self.convert_number(rect.left_top.x),
                "y": self.convert_number(rect.left_top.y),
                "width": self.convert_number((rect.right_bottom.x - rect.left_top.x)),
                "height": self.convert_number((rect.right_bottom.y - rect.left_top.y)),
                "rx": self.convert_number(rect.corner_radius),
                "ry": self.convert_number(rect.corner_radius)
            }
        )
    
    def line_to_tag(self, line: Line2d) -> SVGTag:
        return SVGTag(
            "line",
            {
                "x1": self.convert_number(line.start.x),
                "y1": self.convert_number(line.start.y),
                "x2": self.convert_number(line.end.x),
                "y2": self.convert_number(line.end.y)
            }
        )

    def circle_to_tag(self, circle: Circle2d) -> SVGTag:
        return SVGTag(
            "circle",
            {
                "cx": self.convert_number(circle.center.x),
                "cy": self.convert_number(circle.center.y),
                "r": self.convert_number(circle.radius),
            }
        )

    def ellipse_to_tag(self, ellipse: Ellipse2d) -> SVGTag:
        return SVGTag(
            "ellipse",
            {
                "cx": self.convert_number(ellipse.center.x),
                "cy": self.convert_number(ellipse.center.y),
                "rx": self.convert_number(ellipse.radiuses.width),
                "ry": self.convert_number(ellipse.radiuses.height),
            }
        )

    def polyline_to_tag(self, polyline: Polyline2d) -> SVGTag:
        return SVGTag(
            "polyline",
            {
                "points": " ".join(map(lambda point: "{x}, {y}".format(
                    x=self.convert_number(point.x), 
                    y=self.convert_number(point.y),
                    ), polyline.points))
            }
        )

    def polygon_to_tag(self, polygon: Polygon2d) -> SVGTag:
        return SVGTag(
            "polygon",
            {
                "points": " ".join(map(lambda point: "{x}, {y}".format(
                    x=self.convert_number(point.x), 
                    y=self.convert_number(point.y),
                    ), polygon.points))
            }
        )

    def path_to_tag(self, path: Path2d) -> SVGTag:
        prevPoint: Point2d = None
        path_definition = " ".join(map(lambda component: self.component_to_svg(component, prevPoint), path.components))
        return SVGTag(
            "path",
            {
                "d": path_definition
            }
        )

    def component_to_svg(self, component: Shape2d, prevPoint: Point2d) -> str:
        if isinstance(component, MoveOrigin):
            return self.move_origin_to_svg(component)
        elif isinstance(component, RelMoveOrigin):
            return self.rel_move_origin_to_svg(component)
        elif isinstance(component, HorizontalLine):
            return self.hor_line_to_svg(component)
        elif isinstance(component, RelHorizontalLine):
            return self.rel_hor_line_to_svg(component)
        elif isinstance(component, VerticalLine):
            return self.ver_line_to_svg(component)
        elif isinstance(component, RelVerticalLine):
            return self.rel_ver_line_to_svg(component)
        elif isinstance(component, Line):
            return self.line_to_svg(component)
        elif isinstance(component, RelLine):
            return self.rel_line_to_svg(component)            
        elif isinstance(component, StrugBezier):
            return self.strug_to_svg(component)
        elif isinstance(component, RelStrugBezier):
            return self.rel_strug_to_svg(component)
        elif isinstance(component, CubicBezier):
            return self.cubic_bezier_to_svg(component)
        elif isinstance(component, RelCubicBezier):
            return self.rel_cubic_bezier_to_svg(component)
        elif isinstance(component, Quadratic):
            return self.quadratic_to_svg(component)
        elif isinstance(component, RelQuadratic):
            return self.rel_quadratic_to_svg(component)
        elif isinstance(component, ReflectedQuadratic):
            return self.reflected_quadratic_to_svg(component)
        elif isinstance(component, RelReflectedQuadratic):
            return self.rel_reflected_quadratic_to_svg(component)
        elif isinstance(component, Arc):
            return self.arc_to_svg(component)
        elif isinstance(component, RelArc):
            return self.rel_arc_to_svg(component)
        elif isinstance(component, SimpleArc):
            return self.simple_arc_to_svg(component)
        elif isinstance(component, RelSimpleArc):
            return self.rel_simple_arc_to_svg(component)
        elif isinstance(component, ClosePath):
            return self.close_path_to_svg(component)
        else:
            raise RuntimeError("Not Implemented")
                    

        
    def move_origin_to_svg(self, moveOrigin: MoveOrigin) -> str:
        return "M{x}, {y}".format(
            x=self.convert_number(moveOrigin.target.x), 
            y=self.convert_number(moveOrigin.target.y)
            )

    def rel_move_origin_to_svg(self, relMoveOrigin: RelMoveOrigin) -> str:
        return "m{x}, {y}".format(
            x=self.convert_number(relMoveOrigin.target.dx),
            y=self.convert_number(relMoveOrigin.target.dy)
            )

    def hor_line_to_svg(self, horLine: HorizontalLine) -> str:
        return "H{x}".format(
            x=self.convert_number(horLine.length)
            )

    def rel_hor_line_to_svg(self, horLine: RelHorizontalLine) -> str:
        return "h{x}".format(
            x=self.convert_number(horLine.length)
            )

    def ver_line_to_svg(self, verLine: VerticalLine) -> str:
        return "V{x}".format(
            x=self.convert_number(verLine.length)
            )

    def rel_ver_line_to_svg(self, verLine: RelVerticalLine) -> str:
        return "v{x}".format(
            x=self.convert_number(verLine.length)
            )

    def line_to_svg(self, line: Line) -> str:
        return "L{x}, {y}".format(
            x=self.convert_number(line.target.x), 
            y=self.convert_number(line.target.y)
            )
    
    def rel_line_to_svg(self, line: RelLine) -> str:
        return "l{x}, {y}".format(
            x=self.convert_number(line.target.dx), 
            y=self.convert_number(line.target.dy)
            )

    def cubic_bezier_to_svg(self, cubic_bezier: CubicBezier) -> str:
        return "C{x1} {y1}, {x2} {y2} {x} {y}".format(
            x1=self.convert_number(cubic_bezier.startControlPoint.x),
            y1=self.convert_number(cubic_bezier.startControlPoint.y),
            x2=self.convert_number(cubic_bezier.endControlPoint.x),
            y2=self.convert_number(cubic_bezier.endControlPoint.y),
            x=self.convert_number(cubic_bezier.target.x),
            y=self.convert_number(cubic_bezier.target.y)
        )

    def rel_cubic_bezier_to_svg(self, rel_cubic_bezier: RelCubicBezier) -> str:
        return "c{dx1} {dy1}, {dx2} {dy2} {dx} {dy}".format(
            dx1=self.convert_number(rel_cubic_bezier.startControlPoint.dx),
            dy1=self.convert_number(rel_cubic_bezier.startControlPoint.dy),
            dx2=self.convert_number(rel_cubic_bezier.endControlPoint.dx),
            dy2=self.convert_number(rel_cubic_bezier.endControlPoint.dy),
            dx=self.convert_number(rel_cubic_bezier.target.dx),
            dy=self.convert_number(rel_cubic_bezier.target.dy)
        )

    def strug_to_svg(self, strug_bezier: StrugBezier) -> str:
        return "S{x2} {y2} {x} {y}".format(
            x2=self.convert_number(strug_bezier.endControlPoint.x),
            y2=self.convert_number(strug_bezier.endControlPoint.y),
            x=self.convert_number(strug_bezier.target.x),
            y=self.convert_number(strug_bezier.target.y)
        )
        
    def rel_strug_to_svg(self, rel_strug_bezier: RelStrugBezier) -> str:
        return "s{dx2} {dy2} {dx} {dy}".format(
            dx2=self.convert_number(rel_strug_bezier.endControlPoint.dx),
            dy2=self.convert_number(rel_strug_bezier.endControlPoint.dy),
            dx=self.convert_number(rel_strug_bezier.target.dx),
            dy=self.convert_number(rel_strug_bezier.target.dy)
        )

    def quadratic_to_svg(self, quadratic: Quadratic) -> str:
        return "Q{x1} {y1}, {x2} {y2} {x} {y}".format(
            x1=self.convert_number(quadratic.controlPoint.x),
            y1=self.convert_number(quadratic.controlPoint.y),
            x=self.convert_number(quadratic.target.x),
            y=self.convert_number(quadratic.target.y)
        )

    def rel_quadratic_to_svg(self, rel_quadratic: RelQuadratic) -> str:
        return "q{dx1} {dy1}, {dx2} {dy2} {dx} {dy}".format(
            dx1=self.convert_number(rel_quadratic.controlPoint.dx),
            dy1=self.convert_number(rel_quadratic.controlPoint.dy),
            dx=self.convert_number(rel_quadratic.target.dx),
            dy=self.convert_number(rel_quadratic.target.dy)
        )


    def reflected_quadratic_to_svg(self, reflected_quadratic: ReflectedQuadratic) -> str:
        return "T{x} {y}".format(
            x=self.convert_number(reflected_quadratic.target.x),
            y=self.convert_number(reflected_quadratic.target.y)
        )

    def rel_reflected_quadratic_to_svg(self, rel_reflected_quadratic: RelReflectedQuadratic) -> str:
        return "t{dx} {dy}".format(
            dx=self.convert_number(rel_reflected_quadratic.target.dx),
            dy=self.convert_number(rel_reflected_quadratic.target.dy)
        )

    def arc_to_svg(self, arc: Arc) -> str:
        return "A{rx} {ry} {x_axis_rotation} {large_arc_flag} {sweep_flag} {x} {y}".format(
            rx=self.convert_number(arc.radiuses.width),
            ry=self.convert_number(arc.radiuses.height),
            x_axis_rotation=math.degrees(arc.angle),
            large_arc_flag=1 if arc.large_arc else 0,
            sweep_flag=1 if arc.sweep else 0,
            x=self.convert_number(arc.target.x),
            y=self.convert_number(arc.target.y)
        )

    def rel_arc_to_svg(self, rel_arc: RelArc) -> str:
        return "a{rx} {ry} {x_axis_rotation} {large_arc_flag} {sweep_flag} {dx} {dy}".format(
            rx=self.convert_number(rel_arc.radiuses.width),
            ry=self.convert_number(rel_arc.radiuses.height),
            x_axis_rotation=math.degrees(rel_arc.angle),
            large_arc_flag=1 if rel_arc.large_arc else 0,
            sweep_flag=1 if rel_arc.sweep else 0,
            dx=self.convert_number(rel_arc.target.dx),
            dy=self.convert_number(rel_arc.target.dy)
        )

    def simple_arc_to_svg(self, arc: SimpleArc) -> str:
        return "A{rx} {ry} {x_axis_rotation} {large_arc_flag} {sweep_flag} {x} {y}".format(
            rx=self.convert_number(arc.radius),
            ry=self.convert_number(arc.radius),
            x_axis_rotation=0,
            large_arc_flag=1 if arc.large_arc else 0,
            sweep_flag=0 if arc.cw_direction else 1,
            x=self.convert_number(arc.target.x),
            y=self.convert_number(arc.target.y)
        )

    def rel_simple_arc_to_svg(self, rel_arc: RelSimpleArc) -> str:
        return "a{rx} {ry} {x_axis_rotation} {large_arc_flag} {sweep_flag} {x} {y}".format(
            rx=self.convert_number(rel_arc.radius),
            ry=self.convert_number(rel_arc.radius),
            x_axis_rotation=0,
            large_arc_flag=1 if rel_arc.large_arc else 0,
            sweep_flag=1 if rel_arc.cw_direction else 0,
            x=self.convert_number(rel_arc.target.dx),
            y=self.convert_number(rel_arc.target.dy)
        )

    def close_path_to_svg(self, close_path: ClosePath) -> str:
        return "Z".format()

    def convert_number(self, number: float, use_units: bool = False, use_scale: bool = True) -> str:
        return "{value:.4f}{units}".format(value=number * self.scale if use_scale else 1, units=self.units if use_units else "")