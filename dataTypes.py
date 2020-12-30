from typing import Optional


class Point:
    precision = 4

    def __init__(self, x: float, y: float):
        # self.x = round(x, Point.precision)
        # self.y = round(y, Point.precision)
        self.x = x
        self.y = y

        self.arc = None  # type: Optional[RBNode]
        self.edge = None  # type: Optional[HalfEdge]
        self.orderingY = self.y

    def setOrdering(self, y):
        self.orderingY = y
        # self.orderingY = round(y, Point.precision)

    def toPQ(self) -> tuple[float, 'Point']:
        """returns tuple containing ordering y and point itself, useful if storing in priority queue"""
        return -self.orderingY, self

    def __hash__(self):
        return hash(self.x) * hash(self.y)

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __eq__(self, other):
        # todo do setu moze lepiej by bylo tez sprawdzac arc?
        if other is None:
            return False
        return self.x == other.x and self.y == other.y

    def __gt__(self, other): #todo add to documentation
        if self == other or other is None:
            return False

        return self.x > other.x and self.y > other.y

class HalfEdge:
    def __init__(self):
        self.start = None  # type: Optional[Point]
        self.end = None  # type: Optional[Point]

        self.next = None  # type: Optional[HalfEdge]
        self.prev = None  # type: Optional[HalfEdge]

    def __repr__(self):
        return "[" + str(self.start) + " -> " + str(self.end) + "]"

    def __hash__(self):
        return hash(self.start) * hash(self.end)

    def __eq__(self, other):
        if other is None:
            return False
        return (self.start == other.start and self.end == other.end) or \
               (self.start == other.end and self.end == other.end)


class RBNode:
    def __init__(self, point: Point, color=1, parent=None, left=None, right=None, leftHalfEdge=None,
                 rightHalfEdge=None):
        self.parent = parent  # type: Optional[RBNode]
        self.left = left  # type: Optional[RBNode]
        self.right = right  # type: Optional[RBNode]
        self.color = color

        self.point = point  # type: Point
        self.leftHalfEdge = HalfEdge() if leftHalfEdge is None else leftHalfEdge  # type: Optional[HalfEdge]
        self.rightHalfEdge = HalfEdge() if rightHalfEdge is None else rightHalfEdge  # type: Optional[HalfEdge]
        self.prev = None  # type: Optional[RBNode]
        self.next = None  # type: Optional[RBNode]
        self.triggeredBy = None  # type: Optional[Point]
