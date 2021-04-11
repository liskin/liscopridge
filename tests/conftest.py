import liscopridge.cache


def pytest_configure(config):
    liscopridge.cache._pytest = True
