import click
from typing import List
from laser_offset.file_converters.folder_converter import FolderConverter

@click.command()
@click.argument('source_path', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, allow_dash=True))
@click.argument('target_path', type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True, resolve_path=True, allow_dash=True))
@click.argument('laser_width', type=click.IntRange(min=1, max=999))
@click.option('--svg', '-s', default=False, is_flag=True, show_default="False", help="Output as SVG")
@click.option('--dxf/--no-dxf', '-d/-D', default=True, show_default="True", help="Output as DXF")
def laser_offset(source_path, target_path, laser_width, svg, dxf):
    """Creates new drawings from DXFs with outer and inner offset lines by LASER_WIDTH in μm(microns) ans save them into TARGET_PATH as SVG or DXF.

    SOURCE_PATH is folder with DXFs for batch convertion
    
    TARGET_PATH is folder for results

    LASER_WIDTH is beam diameter in μm(microns) from 1 to 999
    """
    
    print(source_path, target_path, laser_width, svg, dxf)
    converter = FolderConverter(source_path, target_path, laser_width / 2000.0, None, svg, dxf)

    files_to_convert = converter.files_to_convert
    click.echo('\nFiles to convert: ')
    for file_to_convert in files_to_convert:
        click.echo(f"\t{click.format_filename(file_to_convert)}")

    click.echo('\nConverting files...\n')
    
    def convertion_callback(file_name: str, full_path: str, target_files: List[str], completed: bool, index: int, total: int):
        if completed and target_files.__len__() > 0:
            click.echo(f"[ {index+1} / {total} ] {file_name}")
            for target in target_files:
                click.echo(f"\t{target}")

    converter.convert(convertion_callback)
