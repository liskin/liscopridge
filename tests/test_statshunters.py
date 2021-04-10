import re
import textwrap

from boddle import boddle  # type: ignore [import]
import bottle  # type: ignore [import]
from mercantile import Tile  # type: ignore [import]
import pytest

from liscopridge.app import statshunters


@pytest.mark.vcr
def test_activities():
    activities = list(statshunters.fetch_activities("https://www.statshunters.com/share/test"))
    assert set(a['name'] for a in activities) == {'test1', 'test2'}
    assert set(
        a['name'] for a in statshunters.filter_activities_type(activities, 'InlineSkate')
    ) == {'test1'}
    assert set(
        a['name'] for a in statshunters.filter_activities_type(activities, {'Ride', 'InlineSkate'})
    ) == {'test1', 'test2'}
    assert statshunters.get_tiles(activities) == {
        Tile(x=8783, y=5410, z=14),
        Tile(x=8783, y=5411, z=14),
        Tile(x=8783, y=5412, z=14),
        Tile(x=8784, y=5411, z=14),
        Tile(x=8784, y=5412, z=14),
        Tile(x=8785, y=5411, z=14),
        Tile(x=8785, y=5412, z=14),
        Tile(x=8786, y=5411, z=14),
        Tile(x=8787, y=5411, z=14),
        Tile(x=8788, y=5410, z=14),
        Tile(x=8788, y=5411, z=14),
        Tile(x=8789, y=5408, z=14),
        Tile(x=8789, y=5409, z=14),
        Tile(x=8789, y=5410, z=14),
        Tile(x=8789, y=5411, z=14),
        Tile(x=8790, y=5407, z=14),
        Tile(x=8790, y=5408, z=14),
        Tile(x=8791, y=5406, z=14),
        Tile(x=8791, y=5407, z=14),
        Tile(x=8791, y=5408, z=14),
        Tile(x=8792, y=5406, z=14),
        Tile(x=8792, y=5407, z=14),
        Tile(x=8793, y=5407, z=14),
    }


def test_kml_tiles():
    tiles = {
        Tile(x=8783, y=5410, z=14),
        Tile(x=8783, y=5411, z=14),
        Tile(x=8783, y=5412, z=14),
    }

    assert statshunters.kml_tiles(tiles) != ""


def test_route_tiles_kml_error():
    with pytest.raises(bottle.HTTPError) as e:
        with boddle():
            statshunters.route_tiles_kml()
    assert e.value.status.startswith('400')


@pytest.mark.vcr
def test_route_tiles_kml():
    with boddle(params={'share_link': "https://www.statshunters.com/share/test"}):
        kml = statshunters.route_tiles_kml()
        assert kml.startswith("<kml")
        assert len(re.findall("<Placemark", kml)) == 23


@pytest.mark.vcr
def test_route_tiles_kml_filter1():
    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'types': 'Ride',
    }):
        kml = statshunters.route_tiles_kml()
        assert kml.startswith("<kml")
        assert len(re.findall("<Placemark", kml)) == 15


@pytest.mark.vcr
def test_route_tiles_kml_filter2():
    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'types': 'Ride InlineSkate',
    }):
        kml = statshunters.route_tiles_kml()
        assert kml.startswith("<kml")
        assert len(re.findall("<Placemark", kml)) == 23


def test_route_tiles_net_kml():
    with pytest.raises(bottle.HTTPError) as e:
        with boddle():
            statshunters.route_tiles_net_kml()
    assert e.value.status.startswith('400')

    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'types': 'Ride InlineSkate',
    }):
        kml = statshunters.route_tiles_net_kml()
        assert kml == textwrap.dedent("""
            <kml xmlns="http://www.opengis.net/kml/2.2">
              <Document>
                <name>explorer tiles netlink</name>
                <visibility>1</visibility>
                <NetworkLink>
                  <name>explorer tiles</name>
                  <visibility>1</visibility>
                  <Link>
                    <href>http://127.0.0.1/tiles.kml?share_link=https%3A%2F%2Fwww.statshunters.com%2Fshare%2Ftest&amp;types=InlineSkate+Ride</href>
                  </Link>
                </NetworkLink>
              </Document>
            </kml>
        """).lstrip("\n")
