# quad tree class
import random


class QuadNode:
    def __init__(self, x, y, width, height, level):
        # x, y are left upper corner
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = (x + width / 2, y + height / 2)
        self.children = list()
        self.elements = list()
        self.level = level

    def __str__(self):
        return str((self.x, self.y))

    def build(self, depth=5):
        if depth == 0:
            return

        self.children.append(QuadNode(self.x, self.y, self.width/2, self.height/2, self.level+1))
        self.children.append(QuadNode(self.x + self.width / 2, self.y, self.width / 2, self.height / 2, self.level+1))
        self.children.append(QuadNode(self.x, self.y + self.height / 2, self.width / 2, self.height / 2, self.level+1))
        self.children.append(QuadNode(self.x + self.width / 2, self.y + self.height / 2, self.width / 2, self.height / 2, self.level+1))
        for child in self.children:
            child.build(depth-1)

    def add_xy_object(self, x, y, xy_object):
        node = self
        while node.children:
            i, j = 0, 0
            if x > node.center[0]:
                i = 1
            if y > node.center[1]:
                j = 1

            node = node.children[i + 2 * j]

        node.elements.append(xy_object)

    def neighbours(self, x, y):
        node = self
        while node.children:
            i, j = 0, 0
            if x > node.center[0]:
                i = 1
            if y > node.center[1]:
                j = 1

            node = node.children[i + 2 * j]
        return node.elements

    def pop(self, x, y):
        node = self
        while node.children:
            i, j = 0, 0
            if x > node.center[0]:
                i = 1
            if y > node.center[1]:
                j = 1

            node = node.children[i + 2 * j]

        n = 0
        for n, element in enumerate(node.elements):
            if element.rect.x == x and element.rect.y == y:
                break

        element = node.elements.pop(n)
        return element

    def expand_to_level(self, level):
        pass


class XYelement:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str((self.x, self.y))


if __name__ == "__main__":
    qn = QuadNode(0, 0, 600, 600, 0)
    qn.build(4)

