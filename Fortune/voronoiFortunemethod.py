from queue import PriorityQueue
from math import inf
from typing import Optional
from random import uniform

from computing import getConvergencePoint, det
from dataTypes import Point, HalfEdge
from rbTree import RBTree, RBNode


"""
Inspiration:
https://pvigier.github.io/2018/11/18/fortune-algorithm-details.html
"""

class Voronoi:
    def __init__(self, points: set[Point]):
        self.points = points
        self.events = PriorityQueue()  # type: PriorityQueue[tuple[float, Point]]
        self.beachLine = RBTree()
        self.notValidEvents = set()  # type: set[Point]
        self.vertices = set()  # type: set[Point]
        self.listEdges = []  # type: list[HalfEdge]

        self.setBounds()
        for p in points:
            self.events.put(p.toPQ())

    def solve(self):
        while self.events.empty() is False:
            y, p = self.events.get()
            # print(y, p)
            # print(self.notValidEvents)
            # print(p in self.notValidEvents)
            if p in self.notValidEvents:
                continue

            if p in self.points:
                self.handleSiteEvent(p)
            else:
                self.handleCircleEvent(p)

        self.endHalfEdges()

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

    def addCircleEvent(self, leftArc: RBNode, midArc: RBNode, rightArc: RBNode,
                       point: Point):  
        convergencePoint, y = getConvergencePoint(leftArc.point, midArc.point, rightArc.point)

        # print("convergenece point", y, convergencePoint)
        if convergencePoint is None or point is None or y is None:
            return
         
        d1 = det(leftArc.point, midArc.point, rightArc.point) > 0 #counter clockwise
        
        if y > point.y or d1:
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

        #dll
        arc.leftHalfEdge.next = arc.rightHalfEdge
        arc.rightHalfEdge.prev = arc.leftHalfEdge
#         print("removing arc", arc.leftHalfEdge.next, arc.rightHalfEdge.prev)

        self.beachLine.delete(arc)

        #dll
        prevHalfEdge = arc.prev.rightHalfEdge
        nextHalfEdge = arc.next.leftHalfEdge

        self.addEdge(arc.prev, arc.next)

        arc.prev.rightHalfEdge.end = point
        arc.next.leftHalfEdge.start = point

        #dll
        arc.prev.rightHalfEdge.next = prevHalfEdge
        prevHalfEdge.prev = arc.prev.rightHalfEdge
#         print("removing v2", arc.prev.rightHalfEdge, prevHalfEdge)


        nextHalfEdge.next = arc.next.leftHalfEdge
        arc.next.leftHalfEdge.prev = nextHalfEdge
#         print("removing v2", nextHalfEdge, arc.next.leftHalfEdge)

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

    def setBounds(self):
        maxX = max(self.points, key=lambda p: p.x).x
        maxY = max(self.points, key=lambda p: p.y).y
        minX = min(self.points, key=lambda p: p.x).x
        minY = min(self.points, key=lambda p: p.y).y

        # print(maxX, maxY, minX, minY)

        divBy = 10
        addX = (maxX - minY) / divBy
        addY = (maxY - minY) / divBy

        self.lowerLeft = Point(minX - addX, minY - addY)
        self.upperRight = Point(maxX + addX, maxY + addY)

    def getIntersectionWithBox(self, point: Point, direction: Point) -> Optional[Point]:
        def calculatePoint(t: float) -> Point:
            x = point.x + t * direction.x
            y = point.y + t * direction.y
            return Point(x, y)

        t = inf
        intersection = None
        if direction.x > 0:
            t = (self.upperRight.x - point.x) / direction.x
            intersection = calculatePoint(t)
        elif direction.x < 0:
            t = (self.lowerLeft.x - point.x) / direction.x
            intersection = calculatePoint(t)

        if direction.y > 0:
            newT = (self.upperRight.y - point.y) / direction.y
            if newT < t:
                intersection = calculatePoint(newT)
        elif direction.y < 0:
            newT = (self.lowerLeft.y - point.y) / direction.y
            if newT < t:
                intersection = calculatePoint(newT)

        return intersection

    def endHalfEdges(self):
        leftArc = self.beachLine.minimum(self.beachLine.root)
        rightArc = leftArc.next
        while rightArc is not None:
            test = leftArc.rightHalfEdge.end
            if test is None or test.x < self.lowerLeft.x or test.x > self.upperRight.x or \
                    test.y < self.lowerLeft.y or test.y > self.upperRight.y:
                # TODO tutaj mozna skonczyc te krawedzie ktore wychodza poza box
                leftArc = rightArc
                rightArc = rightArc.next
                continue

            x = (leftArc.point.x + rightArc.point.x) / 2
            y = (leftArc.point.y + rightArc.point.y) / 2

            tmpPoint = Point(x, y)

            diffX = leftArc.point.x - rightArc.point.x
            diffY = leftArc.point.y - rightArc.point.y

            orientation = Point(-diffY, diffX)

            intersection = self.getIntersectionWithBox(tmpPoint, orientation)
            self.vertices.add(intersection)

            leftArc.rightHalfEdge.start = intersection
            rightArc.leftHalfEdge.end = intersection

            leftArc = rightArc
            rightArc = rightArc.next


if __name__ == '__main__':
    test = [(5, 60), (20, 10), (40, 80), (60, 40), (80, 75), (75, 20)]
#     test = [(uniform(0,1000), uniform(0,1000)) for _ in range(8)]

    points = set()
    for x, y in test:
        points.add(Point(x, y))

    voronoi = Voronoi(points)

    voronoi.solve()
    from pprint import pprint

    pprint(voronoi.listEdges)
    pprint(voronoi.vertices)


    edge = point.edge
    curr = edge.next
    print()
    print("lista krawedzi dla punktu:",point)
    print(edge)
    while curr != edge:
        if curr is None:
            print("end of list!, HalfEdge was infinite")
        print(curr)
        curr = curr.next

