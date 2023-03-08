from pathlib import Path
import sys
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))
print(sys.path)

from laser_offset.cli.laser_offset_cli import laser_offset

if __name__ == '__main__':
    laser_offset()