from queue import PriorityQueue
from math import inf
from typing import Optional

from computing import getConvergencePoint
from dataTypes import Point, HalfEdge
from rbTree import RBTree, RBNode, display_tree


"""
Inspiration:
https://github.com/pvigier/FortuneAlgorithm/blob/master/src/FortuneAlgorithm.cpp
"""

class Voronoi:
    def __init__(self, points: set[Point]):
        self.points = points
        self.events = PriorityQueue()  # type: PriorityQueue[tuple[float, Point]]
        self.beachLine = RBTree()
        self.notValidEvents = set()  # type: set[Point]
        self.vertices = set()  # type: set[Point]
        self.listEdges = []  # type: list[HalfEdge]

        for p in points:
            self.events.put(p.toPQ())

    def solve(self):
        while self.events.empty() is False:
            y, p = self.events.get()
            # display_tree(self.beachLine.root)
            # print(y, p)
            # print(self.notValidEvents)
            # print(p in self.notValidEvents)
            if p in self.notValidEvents:
                continue

            if p in self.points:
                self.handleSiteEvent(p)
            else:
                self.handleCircleEvent(p)

    def handleSiteEvent(self, point: Point):
        if self.beachLine.isEmpty() is True:
            self.beachLine.createRoot(RBNode(point))
            return

        arcAbove = self.beachLine.getNodeAbove(point)

        # print("arcAbove", arcAbove.point)
        if arcAbove.triggeredBy is not None:
            self.notValidEvents.add(arcAbove.triggeredBy)

        leftArc, midArc, rightArc = self.breakArc(arcAbove, point)

        self.addEdge(leftArc, midArc)

        midArc.rightHalfEdge = midArc.leftHalfEdge
        rightArc.leftHalfEdge = leftArc.rightHalfEdge

        if leftArc.prev is not None:
            self.addCircleEvent(leftArc.prev, leftArc, midArc, point)

        if rightArc.next is not None:
            self.addCircleEvent(midArc, rightArc, rightArc.next, point)

    def breakArc(self, arc: RBNode, point: Point) -> tuple[RBNode, RBNode, RBNode]:
        """
        :param arc: arc to be divided
        :param point: point of division
        :return: left, middle, right arc made by division
        """
        midArc = RBNode(point)
        # print(arc.leftHalfEdge, arc.rightHalfEdge)
        leftArc = RBNode(arc.point, leftHalfEdge=arc.leftHalfEdge)

        rightArc = RBNode(arc.point, rightHalfEdge=arc.rightHalfEdge)
        # print("arc", arc.point, "to mid arc", midArc.point)

        # print("left left", leftArc.leftHalfEdge)
        # print("right right", rightArc.rightHalfEdge)
        self.beachLine.replace(arc, midArc)
        self.beachLine.insertBefore(midArc, leftArc)
        self.beachLine.insertAfter(midArc, rightArc)

        return leftArc, midArc, rightArc

    def checkCircle(self, leftArc: RBNode, midArc: RBNode, rightArc: RBNode,
                    convergencePoint: Point) -> bool:

        leftPointIsMovingRight = leftArc.point.y < midArc.point.y
        rightPointIsMovingRight = midArc.point.y < rightArc.point.y

        leftInitialX = leftArc.point.x if leftPointIsMovingRight else midArc.point.x
        rightInitialX = midArc.point.x if rightPointIsMovingRight else rightArc.point.x

        if ((leftPointIsMovingRight and leftInitialX < convergencePoint.x) or
            ((not leftPointIsMovingRight) and leftInitialX > convergencePoint.x)) is False:
            return False

        if ((rightPointIsMovingRight and rightInitialX < convergencePoint.x) or
            ((not rightPointIsMovingRight) and rightInitialX > convergencePoint.x)) is False:
            return False

        return True

    def addCircleEvent(self, leftArc: RBNode, midArc: RBNode, rightArc: RBNode,
                       point: Point):  # TODO naprawic sprawdzanie
        convergencePoint, y = getConvergencePoint(leftArc.point, midArc.point, rightArc.point)

        # print("convergenece point", y, convergencePoint)
        if y > point.y or self.checkCircle(leftArc, midArc, rightArc, convergencePoint) is False:
            return

        convergencePoint.arc = midArc
        convergencePoint.setOrdering(y)

        midArc.triggeredBy = convergencePoint
        self.events.put(convergencePoint.toPQ())

    def handleCircleEvent(self, point: Point):
        self.vertices.add(point)

        leftArc = point.arc.prev
        midArc = point.arc
        rightArc = point.arc.next

        if leftArc.triggeredBy is not None:
            self.notValidEvents.add(leftArc.triggeredBy)

        if rightArc.triggeredBy is not None:
            self.notValidEvents.add(rightArc.triggeredBy)

        self.removeArc(midArc, point)

        if leftArc.prev is not None:
            self.addCircleEvent(leftArc.prev, leftArc, rightArc, point)
        if rightArc.next is not None:
            self.addCircleEvent(leftArc, rightArc, rightArc.next, point)

    def removeArc(self, arc: RBNode, point: Point):
        arc.prev.rightHalfEdge.start = point
        arc.next.leftHalfEdge.end = point

        arc.leftHalfEdge.end = point
        arc.rightHalfEdge.start = point

        self.beachLine.delete(arc)

        self.addEdge(arc.prev, arc.next)

        arc.prev.rightHalfEdge.end = point
        arc.next.leftHalfEdge.start = point

    def addEdge(self, left: RBNode, right: RBNode):
        # print("from", left.point, "to", right.point)
        def attachEdgeToPoint(point):
            newHalfEdge = HalfEdge()
            if point.edge is None:
                point.edge = newHalfEdge
            self.listEdges.append(newHalfEdge)
            return newHalfEdge

        left.rightHalfEdge = attachEdgeToPoint(left.point)
        right.leftHalfEdge = attachEdgeToPoint(right.point)


def findBounds(points: set[Point]) -> tuple[Point, Point]:
    """:returns tuple of points, lowerLeft and upperRight corner"""
    maxX = max(points, key=lambda p: p.x).x
    maxY = max(points, key=lambda p: p.y).y
    minX = min(points, key=lambda p: p.x).x
    minY = min(points, key=lambda p: p.y).y

    # print(maxX, maxY, minX, minY)

    divBy = 10
    addX = (maxX - minY) / divBy
    addY = (maxY - minY) / divBy

    lowerLeft = Point(minX - addX, minY - addY)
    upperRight = Point(maxX + addX, maxY + addY)

    # print(lowerLeft)
    # print(upperRight)
    return lowerLeft, upperRight


def getIntersectionWithBox(lowerLeft: Point, upperRight: Point, point: Point, direction: Point) -> Optional[Point]:
    def calculatePoint(t: float) -> Point:
        x = point.x + t * direction.x
        y = point.y + t * direction.y
        return Point(x, y)

    t = inf
    intersection = None
    if direction.x > 0:
        t = (upperRight.x - point.x) / direction.x
        intersection = calculatePoint(t)
    elif direction.x < 0:
        t = (lowerLeft.x - point.x) / direction.x
        intersection = calculatePoint(t)

    if direction.y > 0:
        newT = (upperRight.y - point.y) / direction.y
        if newT < t:
            intersection = calculatePoint(newT)
    elif direction.y < 0:
        newT = (lowerLeft.y - point.y) / direction.y
        if newT < t:
            intersection = calculatePoint(newT)

    return intersection


def endHalfEdges(lowerLeft: Point, upperRight: Point, voronoi: Voronoi):
    leftArc = voronoi.beachLine.minimum(voronoi.beachLine.root)
    rightArc = leftArc.next
    while rightArc is not None:
        x = (leftArc.point.x + rightArc.point.x) / 2
        y = (leftArc.point.y + rightArc.point.y) / 2

        tmpPoint = Point(x, y)
        # print(leftArc.rightHalfEdge.end, tmpPoint )

        # print("points", leftArc.point, rightArc.point)
        # print("diff", )
        diffX = leftArc.point.x - rightArc.point.x
        diffY = leftArc.point.y - rightArc.point.y

        orientation = Point(-diffY, diffX)

        # print("direction", orientation)
        intersection = getIntersectionWithBox(lowerLeft, upperRight, tmpPoint, orientation)
        voronoi.vertices.add(intersection)

        leftArc.rightHalfEdge.start = intersection
        rightArc.leftHalfEdge.end = intersection

        leftArc = rightArc
        rightArc = rightArc.next


if __name__ == '__main__':
    test = [(5, 60), (20, 10), (40, 80), (60, 40), (80, 75), (75, 20)]
    points = set()
    for x, y in test:
        points.add(Point(x, y))

    voronoi = Voronoi(points)

    voronoi.solve()
    from pprint import pprint

    # pprint(voronoi.vertices)
    # pprint(voronoi.notValidEvents)

    # pprint(voronoi.eventsSet)

    # display_tree(voronoi.beachLine.root)
    lowerLeft, upperRight = findBounds(points)
    # print("fixing\n\n\n")
    endHalfEdges(lowerLeft, upperRight, voronoi)
    # print("\n\nend of fixing\n\n")
    # pprint(voronoi.listEdges)
    # print("after fixing")
    pprint(voronoi.listEdges)
    pprint(voronoi.vertices)
    # plt.xlim((lowerLeft.x, upperRight.x))
    # plt.ylim((lowerLeft.y, upperRight.y))
    #
    #
    # plt.show()
