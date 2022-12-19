from typing import List, Tuple
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.size2d import Size2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.path2d import Path2d
from laser_offset.geometry_2d.shapes_2d.line2d import Line2d
from laser_offset.geometry_2d.shapes_2d.arc2d import Arc2d

# Converts list of shapes to shape chains
def prepareShapes(shapes: List[Shape2d]) -> List[List[Shape2d]]:
    return list(map(lambda shape: [shape], shapes))

# Finds next shape in chain if possible
def mergeIteration(shapes: List[List[Shape2d]]) -> Tuple[List[List[Shape2d]], bool]:
    parsed_shapes = list()
    result = list()
    has_merged_shapes: bool = False
    for index, shape in enumerate(shapes):
        for secondShape in shapes[index+1:]:
            
            end_point = shape[-1].end
            start_point = secondShape[0].start
            start_point_inv = secondShape[-1].end
            
            if shape in parsed_shapes or secondShape in parsed_shapes:
                continue
            
            if end_point.eq(start_point):
                # # print(shape[-1].index, end_point, ' <-> ', start_point, secondShape[0].index)
                parsed_shapes.append(shape)
                parsed_shapes.append(secondShape)
                result.append(shape+secondShape)
                has_merged_shapes = True
                
            elif end_point.eq(start_point_inv):
                # print(shape[-1].index, end_point, ' <-> ', start_point_inv, secondShape[0].index, ' I')
                parsed_shapes.append(shape)
                parsed_shapes.append(secondShape)
                
                secondShapeRev = secondShape.copy()
                secondShapeRev.reverse()
                
                result.append(shape+list(map(lambda ll: ll.inverse, secondShapeRev)))
                
                has_merged_shapes = True
                
        if not shape in parsed_shapes:
            parsed_shapes.append(shape)
            result.append(shape)

    return (result, has_merged_shapes)

# Mergest list of chains into Paths list
def mergeShapes(shapes: List[List[Shape2d]]) -> List[Path2d]:
    result = list()
    
    for chain in shapes:
        result.append(Path2d.pathFromShapes(chain))
    
    return result 

# Extracts Arcs and Lines for merge leabing existing paths and circles
def extractPathsFromShapes(shapes: List[Shape2d]) -> Tuple[List[Shape2d], List[Shape2d]]:  
    result = list()
    shapes_to_merge = list()
    for shape in shapes:
        if isinstance(shape, Arc2d):
            shapes_to_merge.append(shape)
        elif isinstance(shape, Line2d):
            shapes_to_merge.append(shape)
        else:
            result.append(shape)
                
    return (shapes_to_merge, result)

# Looks at list of shapes to extract path elements for merge
def joinShapesToPathShapes(shapes: List[Shape2d]) -> List[Shape2d]:
    (shapes_to_merge, other_shapes) = extractPathsFromShapes(shapes)
    
    prepared_shapes = prepareShapes(shapes_to_merge)
    end: bool = False
    current_shapes = prepared_shapes.copy()

    while not end:
        current_shapes, has_merged_shapes = mergeIteration(current_shapes)
        end = not has_merged_shapes
        
    result_paths = mergeShapes(current_shapes)
    
    return other_shapes + result_paths

class Canvas2d:

    center: Point2d
    size: Size2d
    shapes: List[Shape2d]

    def __init__(self, center: Point2d, size: Size2d, shapes: List[Shape2d]) -> None:
        self.center = center
        self.size = size
        self.shapes = shapes

    @property
    def relative(self) -> 'Canvas2d':
        relative_shapes = list(map(lambda shape: shape.relative, self.shapes))
        return Canvas2d(self.center, self.size, relative_shapes)
        

    
    def cobineShapesToPaths(self) -> 'Canvas2d':
        shapes = joinShapesToPathShapes(self.shapes)
        return Canvas2d(self.center, self.size, shapes)        