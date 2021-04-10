import bottle  # type: ignore [import]

app = bottle.Bottle()


@app.route('/hello')
@app.route('/hello/<name>')
def hello(name='World'):
    form_name = bottle.request.params.get('name')
    bottle.response.content_type = 'text/plain; charset=UTF-8'
    return f"Hello {form_name if form_name else name}"
