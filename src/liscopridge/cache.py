from pathlib import Path

import appdirs  # type: ignore [import]
import requests  # type: ignore [import]
import requests_cache  # type: ignore [import]

_pytest = False


def requests_cache_filename(subname: str) -> str:
    cache_dir = Path(appdirs.user_cache_dir(appname=__package__)) / 'requests_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return str(cache_dir / subname)


def CachedSession(subname: str, **kwargs) -> requests.Session:
    if _pytest:
        return requests.Session()
    else:
        return requests_cache.CachedSession(cache_name=requests_cache_filename(subname), **kwargs)
