import fastkml.geometry  # type: ignore [import]
import pygeoif.geometry  # type: ignore [import]
import shapely.geometry  # type: ignore [import]


# workaround for https://github.com/cleder/fastkml/issues/100
def fix_shapely_GeometryCollection():
    if (fastkml.geometry.GeometryCollection is pygeoif.geometry.GeometryCollection) \
            and (fastkml.geometry.Polygon is shapely.geometry.Polygon):
        fastkml.geometry.GeometryCollection = shapely.geometry.GeometryCollection
