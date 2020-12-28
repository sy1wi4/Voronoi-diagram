from math import sqrt
from typing import Optional

from dataTypes import Point

def getIntersectionOfParabolas(p1: Point, p2: Point, y: float) -> Point:
    """compute intersection of parabolas from p1 and p2 at x coordinate"""
    if p1.y == p2.y:
        px = (p1.x + p2.x) / 2
    elif p1.y == y:
        px = p1.x
    elif p2.y == y:
        px = p2.x
    else:
        d1 = 0.5 / (p1.y - y)
        d2 = 0.5 / (p2.y - y)

        a = d1 - d2
        b = -2.0 * (d1 * p1.x - d2 * p2.x)
        c = (p1.y ** 2 + p1.x ** 2 - y ** 2) * d1 - (p2.y ** 2 + p2.x ** 2 - y ** 2) * d2

        px = (-b + sqrt(b ** 2 - 4 * a * c)) / (2 * a)

    return Point(px, y)


"""
https://math.stackexchange.com/questions/213658/get-the-equation-of-a-circle-when-given-3-points

"""

def getConvergencePoint(point1: Point, point2: Point, point3: Point) -> tuple[Optional[Point], Optional[float]]:
    # print("points",point1, point2, point3)

    p1 = complex(point1.x, point1.y)
    p2 = complex(point2.x, point2.y)
    p3 = complex(point3.x, point3.y)

    w = (p3 - p1) / (p2 - p1)
    if w.imag == 0:
        return None, None
    c = (p2 - p1) * (w - abs(w) ** 2) / (2j * w.imag) + p1  # type: complex
    r = abs(p1 - c)  # type: float

    center = Point(c.real, c.imag)

    return center, center.y - r