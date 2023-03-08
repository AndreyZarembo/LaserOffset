from typing import Tuple, List, Optional

from laser_offset.geometry_2d.canvas2d import Canvas2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.modifiers.polygon_data import PolygonData
from laser_offset.geometry_2d.shapes_2d.path2d import Path2d
from laser_offset.geometry_2d.shapes_2d.circle2d import Circle2d
from laser_offset.modifiers.segment_operations import expdand_segments, fix_segments, fix_loops, make_shape
from laser_offset.modifiers.modifier import Modifier


class Expand(Modifier):
    
    expand_value: float
    def __init__(self, expand_value: float):
        self.expand_value = expand_value
        
    def perform_expand(self, polygon_data: PolygonData, shape: Shape2d, internal: bool = False) -> Optional[Shape2d]:
        segments = expdand_segments(polygon_data, self.expand_value, internal)
        fixed_segments = fix_segments(polygon_data, segments, self.expand_value, internal)
        has_fixes, segments_with_fixed_loops = fix_loops(fixed_segments)
        result_segments = fix_segments(polygon_data, segments_with_fixed_loops, self.expand_value, internal) if has_fixes else fixed_segments
        
        result_shapes = make_shape(polygon_data, shape.style, result_segments)
        if result_shapes is None:
            return None

        return result_shapes

    def modifyPath(self, shape: Path2d) -> List[Shape2d]:
        if shape.components.__len__() == 2:
            return []

        polygon_data: PolygonData = PolygonData.fromShape(shape)        
        result = [shape]
        exp_shape = self.perform_expand(polygon_data, shape, False)
        if exp_shape is not None:
            result.append(exp_shape)
        int_shape = self.perform_expand(polygon_data, shape, True)
        if int_shape is not None:
            result.append(int_shape)
        return result

    def modifyCircle(self, shape: Circle2d) -> List[Shape2d]:
        result = [shape]
        result.append(Circle2d(shape.style, shape.centerPoint, shape.radius + self.expand_value))
        result.append(Circle2d(shape.style, shape.centerPoint, shape.radius - self.expand_value))
        return result
    
    def modifyShape(self, shape: Shape2d) -> List[Shape2d]:
        if isinstance(shape, Path2d):
            return self.modifyPath(shape)
        elif isinstance(shape, Circle2d):
            return self.modifyCircle(shape)
        else:
            print(f"Unknown shape {type(shape)} {shape}")
            return [shape]
    
    def modifyShapes(self, shapes: List[Shape2d]) -> List[Shape2d]:
        result = list()
            
        for shape in shapes:
            expanded_shapes = self.modifyShape(shape)
            result += expanded_shapes
            
        return result

    def modify(self, canvas: Canvas2d) -> Canvas2d:
        shapes = canvas.shapes.copy()
        modified_shapes = self.modifyShapes(shapes)
        output_canvas = Canvas2d(canvas.center, canvas.size, modified_shapes)
        return output_canvas