from abc import ABC
from codecs import StreamReader

from laser_offset.geometry_2d.canvas2d import Canvas2d


class Importer(ABC):

    def import_canvas(self, relative: bool, reader: StreamReader) -> Canvas2d:
        pass
