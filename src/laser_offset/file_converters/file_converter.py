from typing import List, Optional, Protocol
from pathlib import Path

from laser_offset.exporters.dxf_exporter import DXFExporter
from laser_offset.exporters.svg_exporter import SVGExporter
from laser_offset.importers.dxf_importer import DXFImporter
from laser_offset.importers.svg_importer import SVGImporter

from laser_offset.modifiers.modifier import Modifier
from laser_offset.modifiers.expand import Expand

from laser_offset.geometry_2d.canvas2d import Canvas2d

class FileConverter:

    source_folder: str
    target_folder: str
    
    create_svg: bool
    create_dxf: bool
    
    laser_beam_width: float
    
    dxf_importer: DXFImporter
    svg_importer: SVGImporter
    
    expand_modifier: Modifier
    
    svg_exporter: SVGExporter
    dxf_exporter: DXFExporter

    def __init__(self,
        source_folder: str,
        target_folder: str,
        laser_beam_width: float,
        file_list: Optional[List[str]] = None,

        create_svg: bool = False,
        create_dxf: bool = True
        ) -> None:

        self.laser_beam_width = laser_beam_width
        
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.create_svg = create_svg
        self.create_dxf = create_dxf

        self.dxf_importer = DXFImporter()
        self.svg_importer = SVGImporter()
        self.dxf_exporter = DXFExporter()
        self.svg_exporter = SVGExporter()

        self.expand_modifier = Expand(self.laser_beam_width)

    def convert(self, file_name) -> List[str]:

        result: List[str] = list()
        file_path = self.source_folder+"/"+file_name
        
        with open(file_path, "rt") as input:

            canvas = self.dxf_importer.import_canvas(False, input)
            input.close()
            result_canvas = self.convert_canvas(canvas)

            if self.create_svg:
                target_svg_file = self.save_svg(result_canvas, file_name.replace('.dxf', '.svg').replace('.DXF', '.svg'))
                result.append(target_svg_file)
                                    
            if self.create_dxf:
                target_dxf_file = self.save_dxf(result_canvas, file_name)
                result.append(target_dxf_file)

        return result

    def save_svg(self, canvas: Canvas2d, file_name: str) -> str:
        target_path = self.target_folder
        Path(target_path).mkdir(parents=True, exist_ok=True)
        target_file = target_path+"/"+file_name.replace('.DXF', '.SVG').replace('.dxf', '.svg')
        with open(target_file, "wt") as svg_output:
            self.svg_exporter.export_canvas(canvas, True, svg_output)
            return target_file

    def save_dxf(self, canvas: Canvas2d, file_name: str) -> str:
        target_path = self.target_folder
        Path(target_path).mkdir(parents=True, exist_ok=True)
        target_file = target_path+"/"+file_name
        with open(target_file, "wt") as dxf_output:
            self.dxf_exporter.export_canvas(canvas, True, dxf_output)
            return target_file       
        
    def convert_canvas(self, canvas: Canvas2d) -> Canvas2d:
        modified_canvas = self.modify_canvas(canvas)
        expanded_canvas = self.expanded_canvas(modified_canvas)
        return expanded_canvas
            
    def modify_canvas(self, canvas: Canvas2d) -> Canvas2d:
        combined_canvas = canvas.cobineShapesToPaths()
        return combined_canvas
        
    def expanded_canvas(self, canvas: Canvas2d) -> Canvas2d: 
        expanded_canvas = self.expand_modifier.modify(canvas)
        return expanded_canvas