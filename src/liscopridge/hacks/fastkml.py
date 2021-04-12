import fastkml.geometry  # type: ignore [import]
import shapely.geometry  # type: ignore [import]


# workaround for https://github.com/cleder/fastkml/issues/100
def fix_shapely_GeometryCollection():
    fastkml.geometry.GeometryCollection = shapely.geometry.GeometryCollection
