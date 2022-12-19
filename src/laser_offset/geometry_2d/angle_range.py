from typing import List, Tuple
from laser_offset.geometry_2d.normalize_angle import normalize_angle
from laser_offset.math.float_functions import fge, fzero, fclose, fle
import math


class AngleRange:
    angle_ranges: List[Tuple[float, float]]
    s_g_e: bool
    s_uh: bool
    e_uh: bool
    fn: str
    code: str
    def __init__(self, start_angle: float, end_angle: float, cw: bool):
                
        nsa = normalize_angle(start_angle)
        nea = normalize_angle(end_angle)
        
        self.fns = {
            'cw-0': self.cw_segment_with_zero,
            'cw': self.cw_segment,
            'ccw-0': self.ccw_segment_with_zero,
            'ccw': self.ccw_segment
        }
        
        configs = [
            {'cw': True, 's_g_e': False, 's_uh': True, 'e_uh': True, 'fn': 'cw-0', 'code': '0'},
            {'cw': True, 's_g_e': True, 's_uh': True, 'e_uh': True, 'fn': 'cw', 'code': '1'},
            {'cw': True, 's_g_e': False, 's_uh': False, 'e_uh': False, 'fn': 'cw-0', 'code': '2'},
            {'cw': True, 's_g_e': True, 's_uh': False, 'e_uh': False, 'fn': 'cw', 'code': '3'},
            {'cw': True, 's_g_e': False, 's_uh': True, 'e_uh': False, 'fn': 'cw-0', 'code': '4'},
            {'cw': True, 's_g_e': True, 's_uh': False, 'e_uh': True, 'fn': 'cw', 'code': '5'},

            {'cw': False, 's_g_e': False, 's_uh': True, 'e_uh': True, 'fn': 'ccw', 'code': '6'},
            {'cw': False, 's_g_e': True, 's_uh': True, 'e_uh': True, 'fn': 'ccw-0', 'code': '7'},
            {'cw': False, 's_g_e': False, 's_uh': False, 'e_uh': False, 'fn': 'ccw', 'code': '8'},
            {'cw': False, 's_g_e': True, 's_uh': False, 'e_uh': False, 'fn': 'ccw-0', 'code': '9'},
            {'cw': False, 's_g_e': False, 's_uh': True, 'e_uh': False, 'fn': 'ccw', 'code': 'A'},
            {'cw': False, 's_g_e': True, 's_uh': False, 'e_uh': True, 'fn': 'ccw-0', 'code': 'B'},
        ]
        
        s_g_e = nsa > nea
        s_uh = fge(nsa, 0) and fle(nsa, math.pi)
        e_uh = fge(nea, 0) and fle(nea, math.pi)
        
        self.s_g_e = s_g_e
        self.s_uh = s_uh
        self.e_uh = e_uh
        self.fn = None
        
        for config in configs:
            if config['cw'] == cw and config['s_g_e'] == s_g_e and config['s_uh'] == s_uh and config['e_uh'] == e_uh:
                self.fn = config['fn']
                self.code = config['code']
                break

        if self.fn is None:
            print("Something Wrong {sa} {ea} {cw}".format(sa=nsa, ea=nea, cw=cw))

        
        self.fns[self.fn](nsa, nea)
    
    def cw_segment(self, start_angle: float, end_angle: float):
        self.angle_ranges = [(end_angle, start_angle)]
        
    def ccw_segment(self, start_angle: float, end_angle: float):
        self.angle_ranges = [(start_angle, end_angle)]
    
    def cw_segment_with_zero(self, start_angle: float, end_angle: float):
        self.angle_ranges = [(0, start_angle), (end_angle, 2 * math.pi)]
        
    def ccw_segment_with_zero(self, start_angle: float, end_angle: float):
        self.angle_ranges = [(0, end_angle), (start_angle, 2 * math.pi)]
        
    def has_angle(self, angle: float) -> bool:
        for angle_range in self.angle_ranges:
            if fge(angle, angle_range[0]) and fle(angle, angle_range[1]):
                return True
        return False