from abc import ABC

from typing import List

from laser_offset.geometry_2d.canvas2d import Canvas2d
from laser_offset.geometry_2d.shape2d import Shape2d


class Modifier(ABC):

    def modifyShape(self, shape: Shape2d) -> Shape2d:
        raise RuntimeError('Not Implemented')        
    
    def modifyShapes(self, shapes: List[Shape2d]) -> List[Shape2d]:
        raise RuntimeError('Not Implemented')

    def modify(self, canvas: Canvas2d) -> Canvas2d:
        raise RuntimeError('Not Implemented')