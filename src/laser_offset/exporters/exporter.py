from abc import ABC
from codecs import StreamWriter

from laser_offset.geometry_2d.canvas2d import Canvas2d


class Exporter(ABC):

    def export_canvas(self, canvas: Canvas2d, match_size: bool, stream: StreamWriter):
        raise RuntimeError("Not Implemented")