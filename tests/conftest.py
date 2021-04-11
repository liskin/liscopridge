from webtest import TestApp  # type: ignore [import]

import liscopridge.cache


def pytest_configure(config):
    liscopridge.cache._pytest = True

    # https://github.com/Pylons/webtest/pull/227
    TestApp.__test__ = False
