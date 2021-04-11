import bottle  # type: ignore [import]
import pkg_resources

bottle.TEMPLATE_PATH = [pkg_resources.resource_filename(__package__, "templates")]
