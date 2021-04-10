import bottle  # type: ignore [import]

app = bottle.Bottle()


@app.route('/hello')
def hello():
    return "Hello World"
