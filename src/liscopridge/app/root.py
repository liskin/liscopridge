import bottle  # type: ignore [import]

from . import statshunters

app = bottle.Bottle()
app.mount('/statshunters/', statshunters.app)


@app.get('/hello')
@app.get('/hello/<name>')
def hello(name='World'):
    form_name = bottle.request.params.get('name')
    bottle.response.content_type = 'text/plain; charset=UTF-8'
    return f"Hello {form_name if form_name else name}"
