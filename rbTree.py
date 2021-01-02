from typing import Optional
from math import inf

from computing import getIntersectionOfParabolas
from dataTypes import RBNode, Point

"""
Implementation of red black tree from
https://github.com/keon/algorithms/blob/master/algorithms/tree/red_black_tree/red_black_tree.py
modified to support operations on Arcs, deleted some unused methods
"""

class RBTree:
    def __init__(self):
        self.root = None  # type: Optional[RBNode]

    def createRoot(self, node: RBNode) -> None:
        self.root = node
        node.color = 0

    def isEmpty(self) -> bool:
        return self.root is None

    def getNodeAbove(self, point: Point) -> Optional[RBNode]:
        """returns node above intersection made by point or None if dont exist"""
        if self.isEmpty():
            return None
        node = self.root

        while True:
            leftIntersection = Point(-inf, point.y)
            rightIntersection = Point(inf, point.y)
            # print("       node", node.point, node.prev, node.next)
            if node.prev is not None:
                leftIntersection = getIntersectionOfParabolas(node.prev.point, node.point, point.y)

            if node.next is not None:
                rightIntersection = getIntersectionOfParabolas(node.point, node.next.point, point.y)
            # print("     point", point, "left inter", leftIntersection, "right inter", rightIntersection)
            if point.x < leftIntersection.x:
                node = node.left
            elif point.x > rightIntersection.x:
                node = node.right
            else:
                return node

    def insertBefore(self, beforeNode: RBNode, toInsert: RBNode) -> None:
        if beforeNode.left is None:
            beforeNode.left = toInsert
            toInsert.parent = beforeNode
        else:
            beforeNode.prev.right = toInsert
            toInsert.parent = beforeNode.prev

        toInsert.prev = beforeNode.prev

        if toInsert.prev is not None:
            toInsert.prev.next = toInsert

        toInsert.next = beforeNode
        beforeNode.prev = toInsert

        self.fix_insert(toInsert)

    def insertAfter(self, afterNode: RBNode, toInsert: RBNode) -> None:
        if afterNode.right is None:
            afterNode.right = toInsert
            toInsert.parent = afterNode
        else:
            afterNode.next.left = toInsert
            toInsert.parent = afterNode.next

        toInsert.next = afterNode.next

        if toInsert.next is not None:
            toInsert.next.prev = toInsert

        toInsert.prev = afterNode
        afterNode.next = toInsert

        self.fix_insert(toInsert)

    def replace(self, oldNode: RBNode, newNode: RBNode) -> None:
        self.transplant(oldNode, newNode)
        newNode.left = oldNode.left
        newNode.right = oldNode.right

        if newNode.left is not None:
            newNode.left.parent = newNode

        if newNode.right is not None:
            newNode.right.parent = newNode

        newNode.prev = oldNode.prev
        newNode.next = oldNode.next

        if newNode.prev is not None:
            newNode.prev.next = newNode

        if newNode.next is not None:
            newNode.next.prev = newNode

        newNode.color = oldNode.color

    def left_rotate(self, node):
        # set the node as the left child node of the current node's right node
        right_node = node.right
        if right_node is None:
            return
        else:
            # right node's left node become the right node of current node
            node.right = right_node.left
            if right_node.left is not None:
                right_node.left.parent = node
            right_node.parent = node.parent
            # check the parent case
            if node.parent is None:
                self.root = right_node
            elif node is node.parent.left:
                node.parent.left = right_node
            else:
                node.parent.right = right_node
            right_node.left = node
            node.parent = right_node

    def right_rotate(self, node):
        # set the node as the right child node of the current node's left node
        left_node = node.left
        if left_node is None:
            return
        else:
            # left node's right  node become the left node of current node
            node.left = left_node.right
            if left_node.right is not None:
                left_node.right.parent = node
            left_node.parent = node.parent
            # check the parent case
            if node.parent is None:
                self.root = left_node
            elif node is node.parent.left:
                node.parent.left = left_node
            else:
                node.parent.right = left_node
            left_node.right = node
            node.parent = left_node

    def fix_insert(self, node):
        # case 1 the parent is null, then set the inserted node as root and color = 0
        if node.parent is None:
            node.color = 0
            self.root = node
            return
            # case 2 the parent color is black, do nothing
        # case 3 the parent color is red
        while node.parent and node.parent.color == 1:
            if node.parent is node.parent.parent.left:
                uncle_node = node.parent.parent.right
                if uncle_node and uncle_node.color == 1:
                    # case 3.1 the uncle node is red
                    # then set parent and uncle color is black and grandparent is red
                    # then node => node.parent
                    node.parent.color = 0
                    node.parent.parent.right.color = 0
                    node.parent.parent.color = 1
                    node = node.parent.parent
                    continue
                elif node is node.parent.right:
                    # case 3.2 the uncle node is black or null, and the node is right of parent
                    # then set his parent node is current node
                    # left rotate the node and continue the next
                    node = node.parent
                    self.left_rotate(node)
                # case 3.3 the uncle node is black and parent node is left
                # then parent node set black and grandparent set red
                node.parent.color = 0
                node.parent.parent.color = 1
                self.right_rotate(node.parent.parent)
            else:
                uncle_node = node.parent.parent.left
                if uncle_node and uncle_node.color == 1:
                    # case 3.1 the uncle node is red
                    # then set parent and uncle color is black and grandparent is red
                    # then node => node.parent
                    node.parent.color = 0
                    node.parent.parent.left.color = 0
                    node.parent.parent.color = 1
                    node = node.parent.parent
                    continue
                elif node is node.parent.left:
                    # case 3.2 the uncle node is black or null, and the node is right of parent
                    # then set his parent node is current node
                    # left rotate the node and continue the next
                    node = node.parent
                    self.right_rotate(node)
                # case 3.3 the uncle node is black and parent node is left
                # then parent node set black and grandparent set red
                node.parent.color = 0
                node.parent.parent.color = 1
                self.left_rotate(node.parent.parent)
        self.root.color = 0

    def transplant(self, node_u, node_v):
        """
        replace u with v
        :param node_u: replaced node
        :param node_v:
        :return: None
        """
        if node_u.parent is None:
            self.root = node_v
        elif node_u is node_u.parent.left:
            node_u.parent.left = node_v
        elif node_u is node_u.parent.right:
            node_u.parent.right = node_v
        # check is node_v is None
        if node_v:
            node_v.parent = node_u.parent

    @staticmethod
    def minimum(node) -> RBNode:
        """
        find the minimum node when node regard as a root node
        :param node: starting node
        :return: minimum node
        """
        temp_node = node
        while temp_node.left:
            temp_node = temp_node.left
        return temp_node

    def delete(self, node):
        # find the node position
        # print("deleting", node.point)
        node_color = node.color
        if node.left is None:
            temp_node = node.right
            self.transplant(node, node.right)
        elif node.right is None:
            temp_node = node.left
            self.transplant(node, node.left)
        else:
            # both child exits ,and find minimum child of right child
            node_min = self.minimum(node.right)
            node_color = node_min.color
            temp_node = node_min.right
            ##
            if node_min.parent != node:
                self.transplant(node_min, node_min.right)
                node_min.right = node.right
                node_min.right.parent = node_min
            self.transplant(node, node_min)
            node_min.left = node.left
            node_min.left.parent = node_min
            node_min.color = node.color
        # when node is black, then need to fix it with 4 cases
        if node_color == 0:
            self.delete_fixup(temp_node)

        if node.prev is not None:
            node.prev.next = node.next

        if node.next is not None:
            node.next.prev = node.prev

    def delete_fixup(self, node):
        # 4 cases
        if node is None:
            return

        while node is not self.root and node.color == 0:
            # node is not root and color is black
            if node == node.parent.left:
                # node is left node
                node_brother = node.parent.right

                if node_brother is None:
                    return
                # case 1: node's red, can not get black node
                # set brother is black and parent is red
                if node_brother.color == 1:
                    node_brother.color = 0
                    node.parent.color = 1
                    self.left_rotate(node.parent)
                    node_brother = node.parent.right
                    if node_brother is None:
                        return

                # case 2: brother node is black, and its children node is both black
                if (node_brother.left is None or node_brother.left.color == 0) and (
                        node_brother.right is None or node_brother.right.color == 0):
                    node_brother.color = 1
                    node = node.parent
                else:

                    # case 3: brother node is black , and its left child node is red and right is black
                    if node_brother.right is None or node_brother.right.color == 0:
                        node_brother.color = 1
                        node_brother.left.color = 0
                        self.right_rotate(node_brother)
                        node_brother = node.parent.right
                        if node_brother is None:
                            return

                    # case 4: brother node is black, and right is red, and left is any color
                    node_brother.color = node.parent.color
                    node.parent.color = 0
                    node_brother.right.color = 0
                    self.left_rotate(node.parent)
                    node = self.root

            else:
                node_brother = node.parent.left

                if node_brother is None:
                    return

                if node_brother.color == 1:
                    node_brother.color = 0
                    node.parent.color = 1
                    self.left_rotate(node.parent)

                    if node.parent is None:
                        return

                    node_brother = node.parent.right
                    if node_brother is None:
                        return
                if (node_brother.left is None or node_brother.left.color == 0) and (
                        node_brother.right is None or node_brother.right.color == 0):
                    node_brother.color = 1
                    node = node.parent
                else:
                    if node_brother.left is None or node_brother.left.color == 0:
                        node_brother.color = 1
                        node_brother.right.color = 0
                        self.left_rotate(node_brother)
                        node_brother = node.parent.left
                    node_brother.color = node.parent.color
                    node.parent.color = 0
                    node_brother.left.color = 0
                    self.right_rotate(node.parent)
                node = self.root
                break
        node.color = 0

def printer(node:RBNode): #working on better name for this
    if node is None:
        return str(None)
    return str(node.point)

def toPrint(node: RBNode):
    # return str(node.leftHalfEdge == node.rightHalfEdge)
    return str(node.leftHalfEdge)+" " +str(node.rightHalfEdge)
    # return '%s' % node.point
    # return printer(node.prev) + " " + printer(node) +" " + printer(node.next)

def display_tree(root):
    def print_tree(root):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        # No child.
        if root.right is None and root.left is None:
            line = toPrint(root)
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if root.right is None:
            lines, n, p, x = print_tree(root.left)
            s = toPrint(root)
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if root.left is None:
            lines, n, p, x = print_tree(root.right)
            s = toPrint(root)
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = print_tree(root.left)
        right, m, q, y = print_tree(root.right)
        s = toPrint(root)
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2

    print()
    if root is None:
        return
    lines, _, _, _ = print_tree(root)
    for line in lines:
        print(line)
    print()
