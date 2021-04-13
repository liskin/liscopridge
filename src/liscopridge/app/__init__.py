import bottle  # type: ignore [import]
from pkg_resources import resource_filename

bottle.TEMPLATE_PATH = [resource_filename(__package__, "")]
