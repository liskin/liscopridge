import textwrap

from boddle import boddle  # type: ignore [import]
from webtest import TestApp  # type: ignore [import]

from liscopridge.app import root


def test_hello():
    with boddle():
        assert root.hello() == "Hello World"
        assert root.hello("Tom") == "Hello Tom"

    with boddle(params={'name': "Tom"}):
        assert root.hello() == "Hello Tom"

    webapp = TestApp(root.app)
    assert str(webapp.get("/hello/Tom")) == textwrap.dedent("""
        Response: 200 OK
        Content-Type: text/plain; charset=UTF-8
        Hello Tom
        """).strip('\n')
    assert webapp.get("/hello?name=Tom").body == b"Hello Tom"
