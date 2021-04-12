from shapely.geometry import GeometryCollection  # type: ignore [import]
from shapely.geometry import Polygon  # type: ignore [import]

from liscopridge.util import geometry as ug


def test_polygon_vertical_split():
    ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    int = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)][::-1]
    polygon = Polygon(ext, [int])

    assert ug.polygon_vertical_split(polygon, 1).equals(GeometryCollection([
        Polygon([(0, 0), (0, 2), (1, 2), (1, 1), (0.5, 0.5), (1, 0), (0, 0)]),
        Polygon([(1, 0), (1.5, 0.5), (1.5, 0.5), (1, 1), (1, 2), (2, 2), (2, 0), (1, 0)]),
    ]))
