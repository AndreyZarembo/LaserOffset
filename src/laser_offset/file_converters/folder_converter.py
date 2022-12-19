from typing import List, Optional, Protocol, NamedTuple
from pathlib import Path
import os

from laser_offset.file_converters.file_converter import FileConverter

class FileStatusCallback(Protocol):
    def __call__(self, file_name: str, full_path: str, completed: bool, index: int, total: int) -> None: ...

class FolderConverter:

    source_folder: str
    target_folder: str
    laser_beam_width: float
    file_list: Optional[List[str]] = None

    create_svg: bool = False
    create_dxf: bool = True

    file_converter: FileConverter

    def __init__(self, 
        source_folder: str,
        target_folder: str,
        laser_beam_width: float,
        file_list: Optional[List[str]] = None,

        create_svg: bool = False,
        create_dxf: bool = True
        ) -> None:
        
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.laser_beam_width = laser_beam_width
        self.file_list = file_list
        self.create_svg = create_svg
        self.create_dxf = create_dxf

        self.file_converter = FileConverter(
            source_folder = source_folder,
            target_folder = target_folder,
            create_dxf = create_dxf,
            create_svg = create_svg,
            laser_beam_width = laser_beam_width
        )
        
    @property
    def files_to_convert(self) -> List[str]:
        if self.file_list is not None:
            return self.file_list

        else:
            return list(filter(lambda file_name: file_name.lower().endswith(".dxf") and os.path.isfile(os.path.join(self.source_folder, file_name)), os.listdir(self.source_folder)))

    def convert(self, file_status_callback: FileStatusCallback) -> List[str]:
        files_to_convert = self.files_to_convert

        files_count: int = files_to_convert.__len__()

        for index, file in enumerate(files_to_convert):
            file_path = self.source_folder + "/" + file
            file_status_callback(file, file_path, [], False, index, files_count)

            target_files = self.file_converter.convert(file)

            file_status_callback(file, file_path, target_files, True, index, files_count)
