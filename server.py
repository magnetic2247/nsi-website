from bottle import app, route, template, run, static_file, redirect, response
from bottle.ext.websocket import GeventWebSocketServer, websocket
import bottle_session
import backend.helper as h
import os

# Bottle Session
app = app()
plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
app.install(plugin)

# Index
@route('/')
def index(session):
    return template("frontend/index.html")

# Static Files
@route('/<filename:path>')
def send_static(filename):
    response.set_header('Access-Control-Allow-Origin', '*')
    return static_file(filename, root='frontend/')

# Users
@route('/api/users/:id')
def users(session, id):
    response.set_header('Content-type', 'application/json')
    if id is not None:
        return h.users()
    else:
        return h.users(id)

# Chats
@route('/api/chats/:id')
def chats(session, id):
    response.set_header('Content-type', 'application/json')
    if id is not None:
        return h.chats(id)
    else:
        return "Error"

# Messages
@route('/api/messages/:user_id/:chat_id')
def messages(session, user_id, chat_id):
    response.set_header('Content-type', 'application/json')
    if user_id is not None and chat_id is not None:
        return h.messages(user_id, chat_id)
    else:
        return "Error"

# Start Server
if os.environ.get('APP_LOCATION') == 'heroku':
    run(host="0.0.0.0", port=os.environ.get("PORT", 5000), server=GeventWebSocketServer)
else:
    run(app=app, host="localhost", port=8080, server=GeventWebSocketServer, debug=True, reloader=True)
