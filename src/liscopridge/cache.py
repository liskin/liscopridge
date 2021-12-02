import platformdirs
import requests  # type: ignore [import]
import requests_cache  # type: ignore [import]

_pytest = False


def requests_cache_filename(subname: str) -> str:
    cache_dir = platformdirs.user_cache_path(appname=__package__) / 'requests_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return str(cache_dir / subname)


def CachedSession(subname: str, **kwargs) -> requests.Session:
    if _pytest:
        return requests.Session()
    else:
        return requests_cache.CachedSession(cache_name=requests_cache_filename(subname), **kwargs)
