from pathlib import Path
import sys

import bottle  # type: ignore [import]

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources  # isort: skip
else:
    import importlib_resources  # isort: skip

_template_path = importlib_resources.files(__package__)
assert isinstance(_template_path, Path)
bottle.TEMPLATE_PATH = [str(_template_path)]
