from itertools import chain
from itertools import count
import json
import re
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import Set
from typing import Union
from urllib.parse import urlencode
from urllib.parse import urljoin

import bottle  # type: ignore [import]
import click
import fastkml as kml  # type: ignore [import]
from fastkml import styles as kml_styles  # type: ignore [import]
import mercantile  # type: ignore [import]
from mercantile import Tile  # type: ignore [import]
import shapely.geometry  # type: ignore [import]
import shapely.ops  # type: ignore [import]

from .. import cache
from ..util.geometry import polygon_split_holes

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


def max_square(tiles: Set[Tile], no_overlap: bool = True) -> Set[Tile]:
    max_at: Dict[Tile, int] = {}
    for t in sorted(tiles):
        assert t.z == 14
        n1 = t._replace(x=t.x - 1)
        n2 = t._replace(y=t.y - 1)
        n3 = t._replace(x=t.x - 1, y=t.y - 1)
        if all(n in max_at for n in (n1, n2, n3)):
            sq = min(max_at[n] for n in (n1, n2, n3)) + 1
        else:
            sq = 1
        max_at[t] = sq

    def make_sq(t: Tile, sq: int) -> Set[Tile]:
        return {
            t._replace(x=x, y=y)
            for x in range(t.x, t.x - sq, -1)
            for y in range(t.y, t.y - sq, -1)
        }

    max_sq = max(max_at.values(), default=None)
    max_sq_tiles: Set[Tile] = set()
    for t, sq in max_at.items():
        if sq == max_sq:
            if no_overlap:
                one_larger = make_sq(t._replace(x=t.x + 1, y=t.y + 1), sq + 2)
                if max_sq_tiles & one_larger:
                    continue

            max_sq_tiles |= make_sq(t, sq)

    return max_sq_tiles


def tiles_geometries(tiles: Set[Tile], individual: bool = False, max_sq: bool = False):
    if max_sq:
        max_sq_tiles = max_square(tiles)
        tiles -= max_sq_tiles
        max_sq_geometry = tiles_geometry(max_sq_tiles, individual=individual)
    else:
        max_sq_geometry = None

    geometry = tiles_geometry(tiles, individual=individual)
    return geometry, max_sq_geometry


def tiles_geometry(tiles: Set[Tile], individual: bool = False):
    geometry = shapely.geometry.shape({'type': "GeometryCollection", 'geometries': [
        mercantile.feature(tile)['geometry'] for tile in tiles
    ]})
    if not individual:
        geometry = polygon_split_holes(shapely.ops.unary_union(geometry))
    return geometry


def kml_tiles(geometry, max_sq_geometry=None, individual: bool = False) -> str:
    ns = '{http://www.opengis.net/kml/2.2}'
    k = kml.KML(ns)

    style_normal = kml_styles.Style(id='normal', styles=[
        kml_styles.LineStyle(color="400000ff", width=1),
        kml_styles.PolyStyle(color="300000ff", outline=(1 if individual else 0)),
    ])
    style_max_sq = kml_styles.Style(id='max_sq', styles=[
        kml_styles.LineStyle(color="40ff0000", width=1),
        kml_styles.PolyStyle(color="30ff0000", outline=(1 if individual else 0)),
    ])

    d = kml.Document(ns, name="explorer tiles", styles=[style_normal, style_max_sq])
    k.append(d)

    s = kml.StyleUrl(ns, id="normal")
    p = kml.Placemark(ns, style_url=s, geometry=geometry)
    d.append(p)

    if max_sq_geometry:
        s = kml.StyleUrl(ns, id="max_sq")
        p = kml.Placemark(ns, style_url=s, geometry=max_sq_geometry)
        d.append(p)

    return k.to_string(prettyprint=True)


def kml_netlink(uri: str) -> str:
    ns = '{http://www.opengis.net/kml/2.2}'
    k = kml.KML(ns)

    d = kml.Document(ns, name="explorer tiles netlink")
    k.append(d)

    n = kml.features.NetworkLink(ns, name="explorer tiles", link=kml.links.Link(ns, href=uri))
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

    individual = bottle.request.params.get('individual') is not None
    max_sq = bottle.request.params.get('max_sq') is not None

    activities = fetch_activities(share_link)
    if types:
        activities = filter_activities_type(activities, types)
    tiles = get_tiles(activities)
    geometry, max_sq_geometry = tiles_geometries(tiles, individual=individual, max_sq=max_sq)
    kml = kml_tiles(geometry, max_sq_geometry, individual=individual)

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

    individual = bottle.request.params.get('individual') is not None
    max_sq = bottle.request.params.get('max_sq') is not None

    params = {'share_link': share_link}
    if types:
        params['types'] = ' '.join(sorted(types))
    if individual:
        params['individual'] = individual
    if max_sq:
        params['max_sq'] = max_sq
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


@cli.command('tiles')
@click.argument('share_link', required=True, type=str)
@click.option('-o', '--output', type=click.File('w'), default='-')
@click.option('-f', '--format', 'fmt', type=click.Choice(['kml', 'geojson']), default='geojson')
@click.option('-t', '--types')
@click.option(
    '--individual/--no-individual', default=False,
    help="Show invidual tiles with borders (makes Locus really slow but desktop Google Earth handles it fine)",
)
@click.option(
    '--max-square/--no-max-square', 'max_sq', default=False,
    help="Show max square(s)",
)
def cli_tiles(share_link, output, fmt, types, individual, max_sq):
    types = set(types.split() if types else [])

    activities = fetch_activities(share_link)
    if types:
        activities = filter_activities_type(activities, types)
    tiles = get_tiles(activities)
    geometry, max_sq_geometry = tiles_geometries(tiles, individual=individual, max_sq=max_sq)

    if fmt == 'geojson':
        geojson = shapely.geometry.mapping(geometry)
        json.dump(geojson, output)
    elif fmt == 'kml':
        output.write(kml_tiles(geometry, max_sq_geometry, individual=individual))


if __name__ == "__main__":
    cli()
