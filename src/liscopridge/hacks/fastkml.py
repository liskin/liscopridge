from typing import List

# isort: off

__all__: List[str] = []

import pygeoif  # type: ignore [import]  # noqa: E402
import pygeoif.geometry  # type: ignore [import]  # noqa: E402
import shapely.geometry  # type: ignore [import]  # noqa: E402

# workaround for https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1068290
if not hasattr(pygeoif.geometry, 'as_shape'):
    pygeoif.geometry.as_shape = pygeoif.shape
if not hasattr(shapely.geometry, 'asShape'):
    shapely.geometry.asShape = shapely.geometry.shape

import fastkml.geometry  # type: ignore [import]  # noqa: E402

# workaround for https://github.com/cleder/fastkml/issues/100
if (fastkml.geometry.GeometryCollection is pygeoif.geometry.GeometryCollection) \
        and (fastkml.geometry.Polygon is shapely.geometry.Polygon):
    fastkml.geometry.GeometryCollection = shapely.geometry.GeometryCollection
