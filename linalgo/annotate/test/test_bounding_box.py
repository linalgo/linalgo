# pylint: skip-file
import unittest

from linalgo.annotate import BoundingBox, Vertex


class TestBoundingBox(unittest.TestCase):

    def test_bbox(self):
        a = BoundingBox(left=0, right=4, top=0, bottom=4)
        b = BoundingBox.from_vertex(Vertex(2, 3), height=1, width=1)
        c = BoundingBox(left=6, right=7, top=6, bottom=7)
        print(a, b)
        print(a.contains(b))
        print(a.intersection(b).area)
        print(a.area)
        print(a.overlap(b))
        print(a.intersects(b))
        print(a.intersects(c))
        print(a.intersection(b).area)
