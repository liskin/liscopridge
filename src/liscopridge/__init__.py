import bottle  # type: ignore [import]
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from pkg_resources import resource_filename

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

bottle.TEMPLATE_PATH = [resource_filename(__package__, "templates")]
