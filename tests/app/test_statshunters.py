import re
import textwrap

from boddle import boddle  # type: ignore [import]
import bottle  # type: ignore [import]
from click.testing import CliRunner
from mercantile import Tile  # type: ignore [import]
import pytest  # type: ignore [import]
from webtest import TestApp  # type: ignore [import]

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

    assert statshunters.kml_tiles(statshunters.tiles_geometry(tiles)) != ""


def test_route_tiles_kml_error():
    with pytest.raises(bottle.HTTPError) as e:
        with boddle():
            statshunters.route_tiles_kml()
    assert e.value.status.startswith('400')


@pytest.mark.vcr
def test_route_tiles_kml():
    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'individual': "1",
    }):
        kml = statshunters.route_tiles_kml()
        assert kml.startswith("<kml")
        assert len(re.findall("<Polygon", kml)) == 23


@pytest.mark.vcr
def test_route_tiles_kml_filter1():
    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'types': 'Ride',
        'individual': "1",
    }):
        kml = statshunters.route_tiles_kml()
        assert kml.startswith("<kml")
        assert len(re.findall("<Polygon", kml)) == 15


@pytest.mark.vcr
def test_route_tiles_kml_filter2():
    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'types': 'Ride InlineSkate',
        'individual': "1",
    }):
        kml = statshunters.route_tiles_kml()
        assert kml.startswith("<kml")
        assert len(re.findall("<Polygon", kml)) == 23


@pytest.mark.vcr
def test_route_tiles_kml_maxsq():
    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'max_sq': "1",
    }):
        kml = statshunters.route_tiles_kml()
        assert kml.startswith("<kml")
        assert len(re.findall("<Polygon", kml)) == 7


def test_route_tiles_net_kml_error():
    with pytest.raises(bottle.HTTPError) as e:
        with boddle():
            statshunters.route_tiles_net_kml()
    assert e.value.status.startswith('400')


def test_route_tiles_net_kml():
    with boddle(params={
        'share_link': "https://www.statshunters.com/share/test",
        'types': 'Ride InlineSkate',
    }):
        kml = statshunters.route_tiles_net_kml()
        assert kml == textwrap.dedent("""
            <kml xmlns="http://www.opengis.net/kml/2.2">
              <Document>
                <name>explorer tiles netlink</name>
                <NetworkLink>
                  <name>explorer tiles</name>
                  <Link>
                    <href>http://127.0.0.1/tiles.kml?share_link=https%3A%2F%2Fwww.statshunters.com%2Fshare%2Ftest&amp;types=InlineSkate+Ride</href>
                  </Link>
                </NetworkLink>
              </Document>
            </kml>
        """).lstrip("\n")


def test_route_root():
    webapp = TestApp(statshunters.app)
    assert webapp.get("/").body.startswith(b"<!DOCTYPE html>")


@pytest.mark.vcr
def test_cli_tiles():
    res = CliRunner().invoke(statshunters.cli_tiles, ["https://www.statshunters.com/share/test"])
    assert res.exit_code == 0
    assert len(re.findall("\"Polygon", res.output)) == 1


@pytest.mark.vcr
def test_cli_tiles_kml():
    res = CliRunner().invoke(statshunters.cli_tiles, ["-f", "kml", "https://www.statshunters.com/share/test"])
    assert res.exit_code == 0
    assert len(re.findall("<Polygon", res.output)) == 1
    assert len(re.findall("<outline>0", res.output)) == 2


@pytest.mark.vcr
def test_cli_tiles_individual():
    res = CliRunner().invoke(statshunters.cli_tiles, [
        "--individual", "-f", "kml", "https://www.statshunters.com/share/test"])
    assert res.exit_code == 0
    assert len(re.findall("<Polygon", res.output)) == 23
    assert len(re.findall("<outline>1", res.output)) == 2


def test_max_squares():
    assert statshunters.max_square(set()) == set()

    t1 = {
        Tile(x=1, y=1, z=14),
        Tile(x=1, y=2, z=14),
        Tile(x=2, y=1, z=14),
        Tile(x=2, y=2, z=14),
    }
    t2 = {
        Tile(x=11, y=1, z=14),
        Tile(x=11, y=2, z=14),
        Tile(x=12, y=1, z=14),
        Tile(x=12, y=2, z=14),
    }
    t3 = {
        Tile(x=3, y=1, z=14),
        Tile(x=3, y=2, z=14),
        Tile(x=4, y=1, z=14),
        Tile(x=4, y=2, z=14),
    }
    assert statshunters.max_square(t1) == t1
    assert statshunters.max_square(t1 | {Tile(x=2, y=3, z=14)}) == t1
    assert statshunters.max_square(t1 | t2, no_overlap=True) == t1 | t2
    assert statshunters.max_square(t1 - {Tile(x=1, y=1, z=14)}, no_overlap=False) == t1 - {Tile(x=1, y=1, z=14)}
    assert statshunters.max_square(t1 | t3, no_overlap=False) == t1 | t3
    assert statshunters.max_square(t1 | t3, no_overlap=True) == t1
