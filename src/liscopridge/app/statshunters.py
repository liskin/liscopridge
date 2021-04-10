from itertools import chain
from itertools import count
import re
from typing import Iterable
from typing import Iterator
from typing import Set
from typing import Union
from urllib.parse import urlencode
from urllib.parse import urljoin

import bottle  # type: ignore [import]
from fastkml import kml  # type: ignore [import]
from fastkml import styles as kml_styles  # type: ignore [import]
import mercantile  # type: ignore [import]
from mercantile import Tile  # type: ignore [import]
import requests

app = bottle.Bottle()


def fetch_activities(share_uri: str) -> Iterator[dict]:
    activities_uri = api_activities_uri(share_uri)

    with requests.Session() as s:
        for page in count(1):
            r = s.get(activities_uri, params={'page': page})
            r.raise_for_status()
            activities = r.json()
            if activities['activities']:
                yield from activities['activities']
            else:
                break


def share_uri_validate(share_uri: str) -> None:
    if not re.fullmatch(r"https://www.statshunters.com/share/\w+", share_uri):
        bottle.abort(400, "malformed share uri")


def api_activities_uri(share_uri: str) -> str:
    share_uri_validate(share_uri)
    return share_uri + "/api/activities"


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


def kml_tiles(tiles: Set[Tile]) -> str:
    ns = '{http://www.opengis.net/kml/2.2}'
    k = kml.KML(ns)

    style_normal = kml_styles.Style(id='normal', styles=[
        kml_styles.LineStyle(color="400000ff", width=1),
        kml_styles.PolyStyle(color="300000ff"),
    ])

    d = kml.Document(ns, name="explorer tiles", styles=[style_normal])
    k.append(d)

    for tile in tiles:
        p = kml.Placemark(ns, styleUrl="#normal")
        p.geometry = mercantile.feature(tile)['geometry']
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

    bottle.response.content_type = 'application/vnd.google-earth.kml+xml'
    return kml_tiles(tiles)


@app.post('/tiles-net.kml')
def route_tiles_net_kml() -> str:
    share_link = bottle.request.params.get('share_link')
    if not isinstance(share_link, str):
        bottle.abort(400, "share_link query param required")
    share_uri_validate(share_link)

    types = set(chain.from_iterable(
        t.split() for t in bottle.request.params.getall('types')
    ))

    params = {'share_link': share_link}
    if types:
        params['types'] = ' '.join(sorted(types))
    tiles_uri = urljoin(bottle.request.url, "tiles.kml?" + urlencode(params))

    bottle.response.content_type = 'application/vnd.google-earth.kml+xml'
    bottle.response.set_header('content-disposition', 'attachment')
    return kml_netlink(tiles_uri)


@app.get('/')
def route_root():
    return bottle.static_file('statshunters.html', root=bottle.TEMPLATE_PATH[0])
