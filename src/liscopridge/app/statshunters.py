from itertools import chain
from itertools import count
import json
import re
from typing import Iterable
from typing import Iterator
from typing import Set
from typing import Union
from urllib.parse import urlencode
from urllib.parse import urljoin

import bottle  # type: ignore [import]
import click
from fastkml import kml  # type: ignore [import]
from fastkml import styles as kml_styles  # type: ignore [import]
import mercantile  # type: ignore [import]
from mercantile import Tile  # type: ignore [import]
import shapely  # type: ignore [import]
import shapely.geometry  # type: ignore [import]
import shapely.ops  # type: ignore [import]

from .. import cache
from ..hacks.fastkml import fix_shapely_GeometryCollection

fix_shapely_GeometryCollection()
app = bottle.Bottle()


def fetch_activities(share_link: str) -> Iterator[dict]:
    activities_uri = api_activities_uri(share_link)

    with cache.CachedSession('statshunters', expire_after=900) as s:
        for page in count(1):
            r = s.get(activities_uri, params={'page': page})
            r.raise_for_status()
            activities = r.json()
            if activities['activities']:
                yield from activities['activities']
            else:
                break


def share_link_validate(share_link: str) -> None:
    if not re.fullmatch(r"https://www.statshunters.com/share/\w+", share_link):
        bottle.abort(400, "malformed share uri")


def api_activities_uri(share_link: str) -> str:
    share_link_validate(share_link)
    return share_link + "/api/activities"


def filter_activities_type(activities: Iterable[dict], typ: Union[str, Set[str]]) -> Iterator[dict]:
    if isinstance(typ, set):
        def f(a): return a['type'] in typ
    elif isinstance(typ, str):
        def f(a): return a['type'] == typ

    return filter(f, activities)


def get_tiles(activities: Iterable[dict]) -> Set[Tile]:
    tiles = set()
    for activity in activities:
        for tile in activity['tiles']:
            tiles.add(Tile(**tile, z=14))
    return tiles


def tiles_geometry(tiles: Set[Tile], simplify: bool = False, union: bool = False):
    if simplify:
        tiles = mercantile.simplify(tiles)

    geometry = shapely.geometry.shape({'type': "GeometryCollection", 'geometries': [
        mercantile.feature(tile)['geometry'] for tile in tiles
    ]})

    if union:
        geometry = shapely.ops.unary_union(geometry)

    return geometry


def kml_tiles(geometry: dict) -> str:
    ns = '{http://www.opengis.net/kml/2.2}'
    k = kml.KML(ns)

    style_normal = kml_styles.Style(id='normal', styles=[
        kml_styles.LineStyle(color="400000ff", width=1),
        kml_styles.PolyStyle(color="300000ff"),
    ])

    d = kml.Document(ns, name="explorer tiles", styles=[style_normal])
    k.append(d)

    p = kml.Placemark(ns, styleUrl="#normal")
    p.geometry = geometry
    d.append(p)

    return k.to_string(prettyprint=True)


def kml_netlink(uri: str) -> str:
    ns = '{http://www.opengis.net/kml/2.2}'
    k = kml.KML(ns)

    d = kml.Document(ns, name="explorer tiles netlink")
    k.append(d)

    class NetworkLink(kml.Document):
        __name__ = 'NetworkLink'

        def __init__(self, ns=None, name=None, href=None):
            super().__init__(ns=ns, name=name)
            self._href = href

        def etree_element(self):
            href = kml.etree.Element(ns + "href")
            href.text = self._href

            link = kml.etree.Element(ns + "Link")
            link.append(href)

            e = super().etree_element()
            e.append(link)

            return e

    n = NetworkLink(ns, name="explorer tiles", href=uri)
    d.append(n)

    return k.to_string(prettyprint=True)


@app.get('/tiles.kml')
def route_tiles_kml() -> str:
    share_link = bottle.request.params.get('share_link')
    if not isinstance(share_link, str):
        bottle.abort(400, "share_link query param required")

    types = set(chain.from_iterable(
        t.split() for t in bottle.request.params.getall('types')
    ))

    activities = fetch_activities(share_link)
    if types:
        activities = filter_activities_type(activities, types)
    tiles = get_tiles(activities)
    geometry = tiles_geometry(tiles, simplify=True)  # TODO: configurable
    kml = kml_tiles(geometry)

    bottle.response.content_type = 'application/vnd.google-earth.kml+xml'
    return kml


@app.post('/tiles-net.kml')
def route_tiles_net_kml() -> str:
    share_link = bottle.request.params.get('share_link')
    if not isinstance(share_link, str):
        bottle.abort(400, "share_link query param required")
    share_link_validate(share_link)

    types = set(chain.from_iterable(
        t.split() for t in bottle.request.params.getall('types')
    ))

    params = {'share_link': share_link}
    if types:
        params['types'] = ' '.join(sorted(types))
    tiles_uri = urljoin(bottle.request.url, "tiles.kml?" + urlencode(params))
    kml = kml_netlink(tiles_uri)

    bottle.response.content_type = 'application/vnd.google-earth.kml+xml'
    bottle.response.set_header('content-disposition', 'attachment')
    return kml


@app.get('/')
def route_root():
    return bottle.static_file('statshunters.html', root=bottle.TEMPLATE_PATH[0])


@click.group()
def cli():
    pass


@cli.command('tiles-geojson')
@click.argument('share_link', required=True, type=str)
@click.option('-o', '--output', type=click.File('w'), default='-')
@click.option('-t', '--types')
@click.option('--simplify/--no-simplify', default=False)
@click.option('--union/--no-union', default=False)
def cli_tiles_geojson(share_link, output, types, simplify, union):
    types = set(types.split() if types else [])

    activities = fetch_activities(share_link)
    if types:
        activities = filter_activities_type(activities, types)
    tiles = get_tiles(activities)
    geometry = tiles_geometry(tiles, simplify=simplify, union=union)
    geojson = shapely.geometry.mapping(geometry)

    json.dump(geojson, output)


if __name__ == "__main__":
    cli()
