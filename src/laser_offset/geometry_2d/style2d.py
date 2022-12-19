from laser_offset.geometry_2d.stroke_style import StrokeStyle
from laser_offset.geometry_2d.fill_style import FillStyle

class Style:

    stroke_style: StrokeStyle
    fill_style: FillStyle

    def __init__(self,
        stroke_style: StrokeStyle = StrokeStyle(),
        fill_style: FillStyle = FillStyle()
    ) -> None:
        self.stroke_style = stroke_style
        self.fill_style = fill_style
