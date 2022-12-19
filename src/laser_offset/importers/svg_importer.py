from asyncio import StreamReader
from ctypes import pointer
from re import S
from typing import List, Optional
from laser_offset.geometry_2d.canvas2d import Canvas2d
from laser_offset.geometry_2d.fill_style import FillStyle
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.circle2d import Circle2d
from laser_offset.geometry_2d.shapes_2d.ellipse2d import Ellipse2d
from laser_offset.geometry_2d.shapes_2d.line2d import Line2d
from laser_offset.geometry_2d.shapes_2d.path2d import Arc, ClosePath, CubicBezier, HorizontalLine, Line, MoveOrigin, Path2d, PathComponent, Quadratic, ReflectedQuadratic, RelArc, RelCubicBezier, RelHorizontalLine, RelLine, RelMoveOrigin, RelQuadratic, RelReflectedQuadratic, RelSimpleArc, RelStrugBezier, RelVerticalLine, SimpleArc, StrugBezier, VerticalLine
from laser_offset.geometry_2d.shapes_2d.polygon2d import Polygon2d
from laser_offset.geometry_2d.shapes_2d.polyline2d import Polyline2d
from laser_offset.geometry_2d.shapes_2d.rect2d import Rect2d
from laser_offset.geometry_2d.size2d import Size2d
from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.style2d import Style
from laser_offset.geometry_2d.vector2d import Vector2d
from laser_offset.importers.importer import Importer

import xml.etree.ElementTree as ET

class SVGImporter(Importer):

    def import_canvas(self, relative: bool, reader: StreamReader) -> Canvas2d:
        xml_tree = ET.parse(reader)
        root = xml_tree.getroot()
        if root.tag != '{http://www.w3.org/2000/svg}svg':
            raise RuntimeError("Root should be SVG")

        # TODO: Read Canvas Size
        viewBox = root.attrib.get('viewBox')
        centerPoint = Point2d.cartesian
        size = Size2d(100, 100)
        if viewBox != None:
            coords = viewBox.split(" ")
            if coords.__len__() == 4:
                x1 = float(coords[0])
                y1 = float(coords[1])
                x2 = float(coords[2])
                y2 = float(coords[3])

                size = Size2d(x2-x1, y2-y1)
                centerPoint = Point2d.cartesian((x1+x2)/2, (y1+y2)/2)

        shapes: List[Shape2d] = list()

        for element in root:
            shape = self.parse_element(element)
            if shape is None:
                continue

            style = self.parse_style(element)
            shape.style = style
            shapes.append(shape)


        canvas = Canvas2d(centerPoint, size, shapes)
        return canvas

    def parse_element(self, element: ET.Element) -> Optional[Shape2d]:
        
        if element.tag == '{http://www.w3.org/2000/svg}rectangle':
            return self.parse_rectangle(element)
        elif element.tag == '{http://www.w3.org/2000/svg}line':
            return self.parse_line(element)
        elif element.tag == '{http://www.w3.org/2000/svg}circle':
            return self.parse_circle(element)
        elif element.tag == '{http://www.w3.org/2000/svg}ellipse':
            return self.parse_ellipse(element)
        elif element.tag == '{http://www.w3.org/2000/svg}polyline':
            return self.parse_polyline(element)
        elif element.tag == '{http://www.w3.org/2000/svg}polygon':
            return self.parse_polygon(element)
        elif element.tag == '{http://www.w3.org/2000/svg}path':
            return self.parse_path(element)

    def parse_rectangle(self, element: ET.Element) -> Optional[Rect2d]:
        x = element.attrib.get('x')
        y = element.attrib.get('y')
        width = element.attrib.get('width')
        height = element.attrib.get('height')
        if x is None or y is None or width is None or height is None:
            return None
        
        cx = element.attrib.get('cx')
        return Rect2d(Style(), Point2d.cartesian(x,y), Point2d.cartesian(x+width, y+height), cx if cx is not None else 0)
        
    def parse_line(self, element: ET.Element) -> Optional[Line2d]:
        x1 = element.attrib.get('x1')
        y1 = element.attrib.get('y1')
        x2 = element.attrib.get('x2')
        y2 = element.attrib.get('y2')
        
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None

        return Line2d(Style(), Point2d.cartesian(x1, y1), Point2d.cartesian(x2, y2))

    def parse_circle(self, element: ET.Element) -> Optional[Circle2d]:
        cx = element.attrib.get('cx')
        cy = element.attrib.get('cy')
        r = element.attrib.get('r')

        if cx is None or cy is None or r is None:
            return None
        
        return Circle2d(Style(), Point2d.cartesian(cx,cy), r)

    def parse_ellipse(self, element: ET.Element) -> Optional[Ellipse2d]:
        cx = element.attrib.get('cx')
        cy = element.attrib.get('cy')
        rx = element.attrib.get('rx')
        ry = element.attrib.get('ry')

        if cx is None or cy is None or rx is None or ry is None:
            return None
        
        return Ellipse2d(Style(), Point2d.cartesian(cx,cy), Size2d(rx, ry))

    def preparse_points_string(self, points_string: str) -> str:
        import re

        filtered_points = re.sub(r'(\,[\s\n]*)', ',', points_string)
        points_to_split = re.sub(r'([\s\n]+)', ';', filtered_points)
        return points_to_split

    def parse_points(self, element: ET.Element) -> List[Point2d]:

        points = element.attrib.get('points')
        
        points_to_split = self.preparse_points_string(points)
        
        coord_pairs = points_to_split.split(";")

        points: List[Point2d] = list()
        for coord_pair in coord_pairs:
            coords = coord_pair.split(',')
            if coords.__len__() == 2:
                points.append(Point2d.cartesian(float(coords[0]), float(coords[1])))
        return points

    def parse_polyline(self, element: ET.Element) -> Optional[Polyline2d]:
        points = self.parse_points(element)
        return Polyline2d(Style(), points)

    def parse_polygon(self, element: ET.Element) -> Optional[Polygon2d]:
        points = self.parse_points(element)
        return Polygon2d(Style(), points)

    def parse_path(self, element: ET.Element) -> Optional[Path2d]:
        import re
        
        components_str = element.attrib.get('d')
        splittable_components = re.sub(r'([\s\n]+([MmAaLlQqCcZz]))', ';\g<2>', components_str)

        parsed_components: List[PathComponent] = list()

        for component in splittable_components.split(";"):
            command = component[0]
            points_to_split = self.preparse_points_string(component[1:]).replace(',', ';')
            parsed_component = self.parse_component(command, points_to_split)
            if parsed_component is None:
                continue
            parsed_components.append(parsed_component)

        return Path2d(Style(), parsed_components)

    def parse_component(self, command: str, config: str) -> Optional[PathComponent]:
        if command == 'M':
            return self.parse_M_command(config)
        elif command == 'm':
            return self.parse_m_command(config)
        elif command == 'H':
            return self.parse_H_command(config)
        elif command == 'h':
            return self.parse_h_command(config)
        elif command == 'V':
            return self.parse_V_command(config)
        elif command == 'v':
            return self.parse_v_command(config)
        elif command == 'L':
            return self.parse_L_command(config)
        elif command == 'l':
            return self.parse_l_command(config)
        elif command == 'C':
            return self.parse_C_command(config)
        elif command == 'c':
            return self.parse_c_command(config)
        elif command == 'S':
            return self.parse_S_command(config)
        elif command == 's':
            return self.parse_s_command(config)
        elif command == 'Q':
            return self.parse_Q_command(config)
        elif command == 'q':
            return self.parse_q_command(config)
        elif command == 'T':
            return self.parse_T_command(config)
        elif command == 't':
            return self.parse_t_command(config)
        elif command == 'A':
            return self.parse_A_command(config)
        elif command == 'a':
            return self.parse_a_command(config)
        elif command == 'Z':
            return self.parse_Z_command(config)
        elif command == 'z':
            return self.parse_Z_command(config)



    def parse_M_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 2:
            return None
        return MoveOrigin(Point2d.cartesian(float(parameters[0]), float(parameters[1])))

    def parse_m_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 2:
            return None
        return RelMoveOrigin(Vector2d.cartesian(float(parameters[0]), float(parameters[1])))

    def parse_H_command(self, config: str) -> Optional[PathComponent]:
        return HorizontalLine(float(config))

    def parse_h_command(self, config: str) -> Optional[PathComponent]:
        return RelHorizontalLine(float(config))

    def parse_V_command(self, config: str) -> Optional[PathComponent]:
        return VerticalLine(float(config))

    def parse_v_command(self, config: str) -> Optional[PathComponent]:
        return RelVerticalLine(float(config))

    def parse_L_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 2:
            return None
        return Line(Point2d.cartesian(float(parameters[0]), float(parameters[1])))

    def parse_l_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 2:
            return None
        return RelLine(Point2d.cartesian(float(parameters[0]), float(parameters[1])))

    def parse_C_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 6:
            return None
        return CubicBezier(
            Point2d.cartesian(float(parameters[0]), float(parameters[1])),
            Point2d.cartesian(float(parameters[2]), float(parameters[3])),
            Point2d.cartesian(float(parameters[4]), float(parameters[5])))

    def parse_c_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 6:
            return None
        return RelCubicBezier(
            Vector2d.cartesian(float(parameters[0]), float(parameters[1])),
            Vector2d.cartesian(float(parameters[2]), float(parameters[3])),
            Vector2d.cartesian(float(parameters[4]), float(parameters[5])))

    def parse_S_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 4:
            return None
        return StrugBezier(
            Point2d.cartesian(float(parameters[0]), float(parameters[1])),
            Point2d.cartesian(float(parameters[2]), float(parameters[3])))

    def parse_s_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 4:
            return None
        return RelStrugBezier(
            Vector2d.cartesian(float(parameters[0]), float(parameters[1])),
            Vector2d.cartesian(float(parameters[2]), float(parameters[3])))

    def parse_Q_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 4:
            return None
        return Quadratic(
            Point2d.cartesian(float(parameters[0]), float(parameters[1])),
            Point2d.cartesian(float(parameters[2]), float(parameters[3])))

    def parse_q_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 4:
            return None
        return RelQuadratic(
            Vector2d.cartesian(float(parameters[0]), float(parameters[1])),
            Vector2d.cartesian(float(parameters[2]), float(parameters[3])))

    def parse_T_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 2:
            return None
        return ReflectedQuadratic(
            Point2d.cartesian(float(parameters[0]), float(parameters[1])))

    def parse_t_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 2:
            return None
        return RelReflectedQuadratic(
            Vector2d.cartesian(float(parameters[0]), float(parameters[1])))

    def parse_A_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 7:
            return None

        if parameters[0] == parameters[1]:
            return SimpleArc(
                Point2d.cartesian(float(parameters[5]), float(parameters[6])),
                float(parameters[0]),
                True if parameters[3] == '1' or parameters[3].lower() == 'true' else False,
                True if parameters[4] == '1' or parameters[4].lower() == 'true' else False
                )
        else:
            return Arc(
                Point2d.cartesian(float(parameters[5]), float(parameters[6])),
                Size2d(float(parameters[0]), float(parameters[1])),
                float(parameters[2]),
                True if parameters[3] == '1' or parameters[3].lower() == 'true' else False,
                True if parameters[4] == '1' or parameters[4].lower() == 'true' else False
                )

    def parse_a_command(self, config: str) -> Optional[PathComponent]:
        parameters = config.split(';')
        if parameters.__len__() != 7:
            return None

        if parameters[0] == parameters[1]:
            return RelSimpleArc(
                Point2d.cartesian(float(parameters[5]), float(parameters[6])),
                float(parameters[0]),
                True if parameters[3] == '1' or parameters[3].lower() == 'true' else False,
                True if parameters[4] == '1' or parameters[4].lower() == 'true' else False
                )
        return RelArc(
            Vector2d.cartesian(float(parameters[5]), float(parameters[6])),
            Size2d(float(parameters[0]), float(parameters[1])),
            float(parameters[2]),
            True if parameters[3] == '1' or parameters[3].lower() == 'true' else False,
            True if parameters[4] == '1' or parameters[4].lower() == 'true' else False
            )

    def parse_Z_command(self, config: str) -> Optional[PathComponent]:
        return ClosePath()

    def parse_z_command(self, config: str) -> Optional[PathComponent]:
        return ClosePath()

    def parse_style(self, element: ET.Element) -> Optional[Style]:
        style = Style()
        fill = element.attrib.get('fill')
        if fill is not None:
            style.fill_style = FillStyle(fill)

        stroke = element.attrib.get('stroke')
        if stroke is not None:
            style.stroke_style = StrokeStyle(0.25, stroke)
        
        return style