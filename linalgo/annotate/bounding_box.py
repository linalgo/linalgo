"""Utils to work with bounding boxe annotations."""
from typing import List

from PIL import Image, ImageDraw


# pylint: disable=too-few-public-methods
class Vertex:
    """A simple 2D vertex.

    Parameters
    ----------
    x : float
        The x coordinate of the vertex.
    y : float
        The y coordinate of the vertex.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'({self.x}, {self.y})'


class BoundingBox:
    """A simple 2D bounding box.

    Parameters
    ----------
    left : float
        The left coordinate of the bounding box.
    right : float
        The right coordinate of the bounding box.
    top : float
        The top coordinate of the bounding box.
    bottom : float
        The bottom coordinate of the bounding box.
    """

    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    @staticmethod
    def from_vertex(v: Vertex, height: float, width: float):
        """Instanciate a BoundingBox from a Vertex and a height and width.

        Parameters
        ----------
        v : Vertex
            The vertex to use as the center of the bounding box.
        height : float
            The height of the bounding box.
        width : float
            The width of the bounding box.

        Returns
        -------
        BoundingBox
            The bounding box.
        """
        left = min(v.x, v.x + width)  # width and height can be negative
        right = max(v.x, v.x + width)
        top = min(v.y, v.y + height)
        bottom = max(v.y, v.y + height)
        return BoundingBox(left, right, top, bottom)

    @staticmethod
    def from_vertices(vertices: List[Vertex]):
        """Instanciate a BoundingBox from a list of vertices.

        Parameters
        ----------
        vertices : List[Vertex]
            The vertices to use as the corners of the bounding box.

        Returns
        -------
        BoundingBox
            The bounding box.
        """
        left = min(p.x for p in vertices)
        right = max(p.x for p in vertices)
        top = min(p.y for p in vertices)
        bottom = max(p.y for p in vertices)
        return BoundingBox(left=left, right=right, bottom=bottom, top=top)

    @property
    def height(self):
        """Get the height of the bounding box."""
        return self.bottom - self.top

    @property
    def width(self):
        """Return the width of the bounding box."""
        return self.right - self.left

    @property
    def area(self):
        """Return the area of the bounding box."""
        return self.height * self.width

    @property
    def vertices(self):
        """Return the vertices of the bounding box."""
        return [
            Vertex(self.left, self.top), Vertex(self.right, self.top),
            Vertex(self.right, self.bottom), Vertex(self.left, self.bottom)
        ]

    def contains(self, bbox):
        """Check if the bounding box contains another bounding box.

        Parameters
        ----------
        bbox : BoundingBox
            The bounding box to check.

        Returns
        -------
        bool
            True if the bounding box contains the other bounding box, False otherwise.
        """
        return (self.top <= bbox.top and self.bottom >= bbox.bottom and
                self.left <= bbox.left and self.right >= bbox.right)

    def intersects(self, bbox):
        """Check if the bounding box intersects another bounding box.

        Parameters
        ----------
        bbox : BoundingBox
            The bounding box to check.

        Returns
        -------
        bool
            True if the bounding box intersects the other bounding box, False otherwise.
        """
        c1 = not ((self.top > bbox.bottom) or (bbox.top > self.bottom))
        c2 = not ((self.right < bbox.left) or (bbox.right < self.left))
        return c1 and c2

    def intersection(self, bbox):
        """Get the intersection with another bounding box.

        Parameters
        ----------
        bbox : BoundingBox
            The bounding box to check.

        Returns
        -------
        BoundingBox
            The intersection of the two bounding boxes.
        """
        if not self.intersects(bbox):
            return BoundingBox(0, 0, 0, 0)
        left = max(self.left, bbox.left)
        bottom = min(self.bottom, bbox.bottom)
        right = min(self.right, bbox.right)
        top = max(self.top, bbox.top)
        return BoundingBox(left, right, top, bottom)

    def overlap(self, bbox):
        """Get area of the overlap with another bouding box.

        Parameters
        ----------
        bbox : BoundingBox
            The bounding box to check.

        Returns
        -------
        float
            The area of the overlap of the two bounding boxes.
        """
        if self.area <= 0:
            return 0
        intersection = self.intersection(bbox)
        return intersection.area / self.area

    def __repr__(self):
        return f"{{{', '.join(f'{v}' for v in self.vertices)}}}"


def draw_bounding_boxes(image: Image, annotations: List):
    """Draw bounding boxes on an image

    Parameters
    ----------
    image : PIL.Image
        The image to draw on.
    annotations : List[Annotation]
        The annotations to draw.

    Returns
    -------
    PIL.Image
        The image with the bounding boxes drawn
    """
    draw = ImageDraw.Draw(image)
    for annotation in annotations:
        box = annotation.target.selectors[0]
        color = 'red'
        if annotation.entity.color is not None:
            color = f'#{annotation.entity.color}'
        draw.polygon([
            box.vertices[0].x, box.vertices[0].y,
            box.vertices[1].x, box.vertices[1].y,
            box.vertices[2].x, box.vertices[2].y,
            box.vertices[3].x, box.vertices[3].y],
            None,
            color
        )
    return image


class TextBoundingBoxNavigator:
    """A navigator for bounding boxes for document OCR.

    The bouding boxes are expected to wrap text sections of a document. The 
    navigator makes it easier to get the text covered by each bounding box.

    Parameters
    ----------
    content : List[Annotation]
        The content to navigate.
    layout : List[Annotation]
        The layout to navigate.
    threshold: float
        The threshold to use for the overlap.
    """

    def __init__(self, content, layout, exclude=None, threshold=0.0):
        self._content = content
        self._layout = layout
        self.exclude = exclude
        if self.exclude is None:
            self.exclude = []
        self.threshold = threshold

    def content(self, separator=''):
        """Get the content of the navigator.

        Parameters
        ----------
        separator : str
            The separator to use between the content.

        Returns
        -------
        str
            The content of the navigator.
        """
        content = []
        for b in self._content:
            if b['type'] == 'google' and b['type'] not in self.exclude:
                content.append(b['text'])
        return separator.join(content)

    def get(self, name: str):
        """Get the text content of the navigator.

        Parameters
        ----------
        name : str
            The name of the navigator.

        Returns
        -------
        List[str]
            The text content of the navigator.
        """
        parents = [p for p in self._layout if p['type'] == name]
        navigators = []
        for p in parents:
            ll = [l for l in self._layout if l['bbox'].overlap(p['bbox'])]
            cc = [c for c in self._content if c['bbox'].overlap(
                p['bbox']) > .6]
            n = TextBoundingBoxNavigator(cc, ll, exclude=self.exclude)
            navigators.append(n)
        return navigators


__all__ = [
    'Vertex', 'BoundingBox', 'draw_bounding_boxes', 'TextBoundingBoxNavigator'
]
