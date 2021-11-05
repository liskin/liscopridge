from shapely.geometry import GeometryCollection  # type: ignore [import]
from shapely.geometry import LineString  # type: ignore [import]
import shapely.ops as ops  # type: ignore [import]


def polygon_concat(ps):
    return GeometryCollection([q for p in ps for q in (p.geoms if hasattr(p, 'geoms') else [p])])


def polygon_vertical_split(p, cut_x):
    assert p.geom_type == 'Polygon'

    min_x, min_y, max_x, max_y = p.bounds
    assert min_x < cut_x < max_x

    return ops.split(p, LineString([(cut_x, min_y), (cut_x, max_y)]))


def polygon_split_holes(p):
    if hasattr(p, 'geoms'):
        return polygon_concat(polygon_split_holes(q) for q in p.geoms)
    elif p.geom_type == 'Polygon' and p.interiors:
        cut_x = p.interiors[0].centroid.x
        return polygon_split_holes(polygon_vertical_split(p, cut_x))
    else:
        return p
