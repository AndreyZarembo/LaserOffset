from typing import List, Tuple, Optional
import math

from laser_offset.modifiers.polygon_data import PolygonData, ShapeSegment
from laser_offset.geometry_2d.style2d import Style
from laser_offset.geometry_2d.shape2d import Shape2d
from laser_offset.geometry_2d.vector2d import Vector2d
from laser_offset.geometry_2d.normalize_angle import normalize_angle
from laser_offset.math.float_functions import fzero, fclose, fle
from laser_offset.geometry_2d.shapes_2d.path2d import Path2d, SimpleArc, MoveOrigin, ClosePath, Line
from laser_offset.geometry_2d.arc_segment_2d import ArcSegment2d
from laser_offset.geometry_2d.segment_2d import Segment2d
from laser_offset.geometry_2d.arc_info import ArcInfo
from laser_offset.geometry_2d.shapes_2d.path2d import PathComponent

def expdand_segments(polygon_data: PolygonData, shift_distance: float, internal: bool = False) -> List[ShapeSegment]:

    ext_segments: List[ShapeSegment] = list()
    shift_sign = (1 if polygon_data.clockwise else -1) * (-1 if internal else 1)
    radius_sign = (1 if polygon_data.clockwise else -1)

    # External segments
    for index, segment in enumerate(polygon_data.segments):

        start_shift_vector = Vector2d.polar( shift_distance, normalize_angle(segment.start_vector.da + shift_sign * math.pi / 2 ))
        end_shift_vector = Vector2d.polar( shift_distance, normalize_angle(segment.end_vector.da + shift_sign * math.pi / 2 ))

        new_start_point = segment.start_point + start_shift_vector
        new_end_point = segment.end_point + end_shift_vector
        
        prev_segment = polygon_data.segments[index-1]
        
        angle_range = 5 * math.pi / 180

        on_line = fclose(prev_segment.end_vector.da, segment.start_vector.da, angle_range) or \
                  fclose(prev_segment.end_vector.da, segment.start_vector.da - 2 * math.pi, angle_range) or \
                  fclose(prev_segment.end_vector.da - 2 * math.pi, segment.start_vector.da, angle_range)

        if not on_line and not segment.is_arc and segment.start_point.distance(segment.end_point) < shift_distance:
            new_start_point += segment.start_vector.inverted.single_vector * (shift_distance)
            new_end_point += segment.end_vector.single_vector * (shift_distance)

        if segment.is_arc:
            
            new_radius = segment.component.radius + shift_distance * (-1 if not polygon_data.clockwise == segment.component.cw_direction else 1) * (-1 if internal else 1)
            
            if fzero(new_radius) or new_radius < 0:
                continue
                        
            new_arc = SimpleArc(new_end_point, new_radius, segment.component.cw_direction, segment.component.large_arc)
            
            ext_segments.append(ShapeSegment(
                component=new_arc,
                start_point=new_start_point,
                end_point=new_end_point,
                start_vector=segment.start_vector,
                end_vector=segment.end_vector,
                is_arc=True
            ))
        
        else:
            
            new_line = Line(new_end_point)

            ext_segments.append(ShapeSegment(
                component=new_line,
                start_point=new_start_point,
                end_point=new_end_point,
                start_vector=segment.start_vector,
                end_vector=segment.end_vector,
                is_arc=False
            ))
            
    return ext_segments


# ---- ---- ---- ---- ---- ----


def fix_segments(polygon_data: PolygonData, new_segments: List[ShapeSegment], shift_distance: float, internal: bool = False) -> List[ShapeSegment]:
    
    if new_segments.__len__() == 0:
        return []
    
    result: List[ShapeSegment] = list()
    prev_segment = new_segments[-1]
    
    first_segment_fix = None
    for index, segment in enumerate(new_segments):
        
        fixed_segment = segment
        
        if prev_segment.is_arc:
            ab = ArcSegment2d.fromArc(prev_segment.start_point, prev_segment.component)
        else:
            ab = Segment2d(prev_segment.start_point, prev_segment.end_point)
            
        if segment.is_arc:
            cd = ArcSegment2d.fromArc(segment.start_point, segment.component)
        else:
            cd = Segment2d(segment.start_point, segment.end_point)
        
        intersections = ab.intersection(cd)
                
        if intersections.__len__() == 1:
            intersection = intersections[0]
            
            if segment.is_arc:
                fixed_segment = ShapeSegment(
                    SimpleArc(segment.component.target, segment.component.radius, segment.component.cw_direction, segment.component.large_arc), 
                    intersection, 
                    segment.end_point, 
                    segment.start_vector, 
                    segment.end_vector,
                    segment.is_arc
                )
            else:
                fixed_segment = ShapeSegment(Line(segment.component.target), intersection, segment.end_point, segment.start_vector, segment.end_vector, segment.is_arc)

            if prev_segment.is_arc:
                fixed_prev_segment = ShapeSegment(
                    SimpleArc(intersection, prev_segment.component.radius, prev_segment.component.cw_direction, prev_segment.component.large_arc), 
                    prev_segment.start_point, 
                    intersection,
                    prev_segment.start_vector, 
                    prev_segment.end_vector, 
                    prev_segment.is_arc
                )
            else:
                fixed_prev_segment = ShapeSegment(Line(intersection), prev_segment.start_point, intersection, prev_segment.start_vector, prev_segment.end_vector, prev_segment.is_arc)

            if result.__len__() != 0:
                result[-1] = fixed_prev_segment
            else:
                first_segment_fix = fixed_prev_segment

        else:         
            arc_direction: bool = internal ^ (not polygon_data.clockwise)
            points_distance = segment.start_point.distance(prev_segment.end_point)
            if not fzero(points_distance):
                                  
                segmentVector = Vector2d.fromTwoPoints(prev_segment.end_point, segment.start_point)
                angle_range = 5 * math.pi / 180
                
                on_line = fclose(prev_segment.end_vector.da, segment.start_vector.da, angle_range) or \
                          fclose(prev_segment.end_vector.da, segment.start_vector.da - 2 * math.pi, angle_range) or \
                          fclose(prev_segment.end_vector.da - 2 * math.pi, segment.start_vector.da, angle_range)
                                
                arc_proposal = SimpleArc(segment.start_point, shift_distance, not arc_direction, False)
                arc_info = ArcInfo.fromArc(prev_segment.end_point, arc_proposal.target, arc_proposal.radius, arc_proposal.large_arc, arc_proposal.cw_direction)
                                                                    
                if fle(segment.start_point.distance(prev_segment.end_point), shift_distance) and on_line and arc_info.radius <= shift_distance:
                    result.append(ShapeSegment(Line(segment.start_point), prev_segment.end_point, segment.start_point, prev_segment.end_vector, segment.start_vector, False))
                else:
                    result.append(ShapeSegment(SimpleArc(segment.start_point, shift_distance, not arc_direction, False), prev_segment.end_point, segment.start_point, prev_segment.end_vector, segment.start_vector, True))

        if index == new_segments.__len__() - 1 and first_segment_fix is not None:
            fixed_segment = ShapeSegment(
                first_segment_fix.component, 
                fixed_segment.start_point,
                first_segment_fix.end_point,
                fixed_segment.start_vector,
                fixed_segment.end_vector,
                fixed_segment.is_arc
            )

        result.append(fixed_segment)
            
        prev_segment = fixed_segment
        
    return result


# ---- ---- ---- ---- ---- ----


def fix_loops(segments: List[ShapeSegment]) -> Tuple[bool, List[ShapeSegment]]:
            
    items_to_remove: List[int] = list()
    
    for index, segment in enumerate(segments):
        
        for prev_index, prev_segment in enumerate(segments[:index]):
                    
            if prev_segment.is_arc:
                ab = ArcSegment2d.fromArc(prev_segment.start_point, prev_segment.component)
            else:
                ab = Segment2d(prev_segment.start_point, prev_segment.end_point)

            if segment.is_arc:
                cd = ArcSegment2d.fromArc(segment.start_point, segment.component)
            else:
                cd = Segment2d(segment.start_point, segment.end_point)
                
            intersections = ab.intersection(cd)
                        
            if intersections.__len__() >= 1 and abs(prev_index-index) > 1 and not (index == segments.__len__() -1 and prev_index == 0):
                items_to_remove.append(range(prev_index+1, index))
    
    if items_to_remove.__len__() == 0:
        return (False, segments)

    result_indexes = list()
    for items_range in items_to_remove:
        result_indexes += list(items_range)
    
    new_segments = [i for j, i in enumerate(segments) if j not in result_indexes]
    
    return (True, new_segments)


# ---- ---- ---- ---- ---- ----


def make_shape(polygon_data: PolygonData, style: Style, shape: List[ShapeSegment]) -> Optional[Shape2d]:

    components: List[PathComponent] = list()

    if shape.__len__() == 0:
        return None
        
    for segment in shape:
        components.append(segment.component)
        
    components.insert(0, MoveOrigin(shape[0].start_point))
    components.append(ClosePath())
    
    return Path2d(style, components)