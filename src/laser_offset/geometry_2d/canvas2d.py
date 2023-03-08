from typing import List, Tuple
from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.size2d import Size2d
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.shapes_2d.path2d import Path2d, Arc, SimpleArc, Line
from laser_offset.geometry_2d.shapes_2d.line2d import Line2d
from laser_offset.geometry_2d.shapes_2d.arc2d import Arc2d

from laser_offset.geometry_2d.bounds_rect_2d import BoundsRect2d

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
        elif isinstance(shape, Path2d):
            path2d: Path2d = shape
            if path2d.isClosed:
                result.append(shape)
            else:
                shapes_to_merge += extractComponentsFromPath(path2d)
        else:
            result.append(shape)
                
    return (shapes_to_merge, result)

def extractComponentsFromPath(path: Path2d) -> List[Shape2d]:
    result: List[Shape2d] = []
    current_point = path.start
    for component in path.components:
        if isinstance(component, SimpleArc):
            arc: SimpleArc = component
            result.append(Arc2d(path.style, current_point, arc.target, Size2d(arc.radius, arc.radius), 0, arc.large_arc, arc.cw_direction))
            current_point = arc.target

        elif isinstance(component, Arc):
            arc: Arc = component
            result.append(Arc2d(path.style, current_point, arc.target, arc.radiuses, arc.angle, arc.large_arc, arc.sweep))
            current_point = arc.target

        elif isinstance(component, Line):
            line: Line = component
            new_line = Line2d(path.style, current_point, line.target)
            result.append(new_line)
            current_point = line.target

    return result


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

    @property
    def maxBoundary(self) -> BoundsRect2d:
        minX = 10000
        minY = 10000
        maxX = -10000
        maxY = -10000
        for shape in self.shapes:
            bounds = shape.maxBoundary
            minX = min(minX, bounds.minX)
            minY = min(minY, bounds.minY)
            maxX = max(maxX, bounds.maxX)
            maxY = max(maxY, bounds.maxY)
        s = max(maxX - minX, maxY - minY) * 0.05
        return BoundsRect2d(minX - s, minY - s, maxX + s, maxY + s)

    def updateCenterAndSizeFromBounds(self) -> 'Canvas2d':
        bounds = self.maxBoundary
        return Canvas2d(Point2d.cartesian((bounds.maxX + bounds.minX)/2, (bounds.maxY + bounds.minY)/2),
                        Size2d(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY),
                        self.shapes
                        )
    
    def cobineShapesToPaths(self) -> 'Canvas2d':
        shapes = joinShapesToPathShapes(self.shapes)
        return Canvas2d(self.center, self.size, shapes)        