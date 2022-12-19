from laser_offset.geometry_2d.point2d import Point2d
from laser_offset.geometry_2d.vector2d import Vector2d
from laser_offset.geometry_2d.size2d import Size2d
from typing import NamedTuple
import math

class ArcInfo(NamedTuple):
    center: Point2d
    startAngle: float
    endAngle: float
    deltaAngle: float
    cw: bool
    startVector: Vector2d
    endVector: Vector2d
    radius: float

    def __str__(self) -> str:
        return "ArcInfo\n\tcenter:\t{center}\n\tstart angle:\t{sa}\n\tend angle:\t{ea}\n\tclockwise:\t{cw}\n\tradius:\t{r}".format(
            center=self.center,
            sa=self.startAngle,
            ea=self.endAngle,
            cw=self.cw,
            r=self.radius
        )
    
    def fromArc(start_point: Point2d, end_point: Point2d, radius: float, large_arc: bool, cw_direction: bool) -> 'ArcInfo':

        def radian(ux: float, uy: float, vx: float, vy: float):
            dot: float = ux * vx + uy * vy
            mod: float = math.sqrt( ( ux * ux + uy * uy ) * ( vx * vx + vy * vy ) )
            rad: float = math.acos( dot / mod )
            if ux * vy - uy * vx < 0.0:
                rad = -rad

            return rad

        x1: float = start_point.x
        y1: float = start_point.y
        rx: float = radius
        ry: float = radius
        phi: float = 0
        fA: float = not large_arc
        fS: float = cw_direction
        x2: float = end_point.x
        y2: float = end_point.y

        PIx2: float = math.pi * 2.0
    #var cx, cy, startAngle, deltaAngle, endAngle;
        if rx < 0:
            rx = -rx

        if ry < 0:
            ry = -ry

        if rx == 0.0 or ry == 0.0:
            raise RuntimeError('Raidus can not be zero')


        s_phi: float = math.sin(phi)
        c_phi: float = math.cos(phi)
        hd_x: float = (x1 - x2) / 2.0 # half diff of x
        hd_y: float = (y1 - y2) / 2.0 # half diff of y
        hs_x: float = (x1 + x2) / 2.0 # half sum of x
        hs_y: float = (y1 + y2) / 2.0 # half sum of y

        # F6.5.1
        x1_: float = c_phi * hd_x + s_phi * hd_y
        y1_: float = c_phi * hd_y - s_phi * hd_x

        # F.6.6 Correction of out-of-range radii
        # Step 3: Ensure radii are large enough
        lambda_: float = (x1_ * x1_) / (rx * rx) + (y1_ * y1_) / (ry * ry)
        if lambda_ > 1:
            rx = rx * math.sqrt(lambda_)
            ry = ry * math.sqrt(lambda_)

        rxry: float = rx * ry
        rxy1_: float = rx * y1_
        ryx1_: float = ry * x1_

        sum_of_sq: float = rxy1_ * rxy1_ + ryx1_ * ryx1_ # sum of square
        if sum_of_sq == 0:
            raise RuntimeError('start point can not be same as end point ', start_point.__str__(), radius)

        coe: float = math.sqrt(abs((rxry * rxry - sum_of_sq) / sum_of_sq))
        if fA == fS:
            coe = -coe

        # F6.5.2
        cx_: float = coe * rxy1_ / ry
        cy_: float = -coe * ryx1_ / rx

        # F6.5.3
        cx = c_phi * cx_ - s_phi * cy_ + hs_x
        cy = s_phi * cx_ + c_phi * cy_ + hs_y

        xcr1: float = (x1_ - cx_) / rx
        xcr2: float = (x1_ + cx_) / rx
        ycr1: float = (y1_ - cy_) / ry
        ycr2: float = (y1_ + cy_) / ry

        # F6.5.5
        startAngle: float = radian(1.0, 0.0, xcr1, ycr1)

        # F6.5.6
        deltaAngle = radian(xcr1, ycr1, -xcr2, -ycr2)
        while deltaAngle > PIx2:
            deltaAngle -= PIx2

        while deltaAngle < 0.0:
            deltaAngle += PIx2

        if fS == False or fS == 0:
            deltaAngle -= PIx2

        endAngle = startAngle + deltaAngle
        while endAngle > PIx2:
            endAngle -= PIx2
        while endAngle < 0.0: 
            endAngle += PIx2

        rotationSign: float = 1 if fS else -1

        angle_shift = math.pi/2 * (-1 if cw_direction else 1)
            
        startVector: Vector2d = Vector2d.polar(1, startAngle + angle_shift)
        endVector: Vector2d = Vector2d.polar(1, endAngle + angle_shift)

        outputObj: ArcInfo = ArcInfo(
            Point2d.cartesian(cx, cy),
            startAngle,
            endAngle,
            deltaAngle,
            fS == True or fS == 1,
            startVector,
            endVector,
            radius
            )

        return outputObj
