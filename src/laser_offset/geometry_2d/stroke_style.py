
from enum import Enum
from typing import List


class StrokeLineCap(Enum):
    ROUND = 0
    BUTT = 1
    SQUARE = 2

class StrokeLineJoint(Enum):
    ROUND = 0
    MITER = 1
    BEVEl = 2

class StrokeStyle:

    width: float
    color: str
    line_cap: StrokeLineCap
    line_joint: StrokeLineJoint
    mitter_limit: float
    dash: List[float]

    def __init__(self,
        width: float = 0.15,
        color: str = "black",
        line_cap: StrokeLineCap = StrokeLineCap.ROUND,
        line_joint: StrokeLineJoint = StrokeLineJoint.ROUND,
        mitter_limit: float = 0,
        dash: List[float] = list() 
    ) -> None:
        self.width = width
        self.color = color
        self.line_cap = line_cap
        self.line_joint = line_joint
        self.mitter_limit = mitter_limit
        self.dash = dash
