import bottle_session, bottle
from bottle import route, template, run, request, response, static_file, get, post, redirect
from bottle.ext.websocket import GeventWebSocketServer, websocket
import helper as h
import json, html, sys, os

# Bottle App with Session plugin
app = bottle.app()
plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
app.install(plugin)

# Index
@route('/')
def index():
    return template("frontend/index.html")

# Chat page
@route('/chat')
def chat():
    return template("frontend/chat/index.html")

# Login page
# Normal GET request
@route('/login')
def login():
    # Register Page
    if "register" in request.query:
        return template("frontend/login/register.html") 
    # Login page
    else:
        return template("frontend/login/login.html")
# POST Request
@route('/login', method="POST")
def post_login(session):
    passwd = request.forms.get("pass")
    login = request.forms.get("login")
    if login is not None and passwd is not None:
        # Register User
        if "register" in request.query:
            data = h.register(login, passwd)
            session['id'] = json.loads(data[1])["id"]
            session['username'] = login
            session['password'] = passwd
            print("Register with credentials", login, passwd)
        # Login User
        else:
            data = h.login(login, passwd)
            if data[0]:
                session['id'] = json.loads(data[1])["id"]
                session['username'] = login
                session['password'] = passwd
                print("Login with credentials", login, passwd)
                return redirect('/chat')
            else:
                print("Failed login with credentials", login, passwd, "and data", data)
    else:
        return redirect("/")

# API
# Check if username taken
@route('/api/username/<user>')
def api_check_user(user):
    if h.users(user) == "{}":
        return "ok"
    return "taken"


# Static Files
@route('/<filename:path>')
def static_index(filename):
    response.set_header('Access-Control-Allow-Origin', '*')
    return static_file(filename, root='frontend/')

# Web Sockets
users = set()
msgs = []
@route('/socket', apply=[websocket])
def wsocket(ws):
    # Global Messages Array
    global msgs

    try:
        # New Client
        users.add(ws)

        # Keep Connecttion Alive
        while True:
            # Receive Message
            msg = ws.receive()
            # Check if client still connected
            if msg is not None:
                # Client requests all messages
                if msg == "all":
                    for m in msgs:
                        ws.send(m)
                # Client sends message
                else:
                    # Escape Message
                    escaped_msg = html.escape(msg, quote=False)

                    # Process JSON
                    data_json = json.loads(escaped_msg)

                    # Add message to array
                    msgs.append(escaped_msg)

                    # Send message to all conneted clients
                    for u in users:
                        u.send(escaped_msg)

                    # Log
                    print("Message from", data_json["usrname"],":", data_json["message"])
            else:
                # Client Disconnected
                break
        # Remove Disconnected Client
        users.remove(ws)
    # Error! Restart Script
    except Exception as e:
        print("Error:", e)
        print("Restarting script...")
        os.execv(sys.argv[0], sys.argv)


# Start Server
if os.environ.get('APP_LOCATION') == 'heroku':
    run(app=app, host="0.0.0.0", port=os.environ.get("PORT", 5000), server=GeventWebSocketServer)
else:
    run(app=app, host='localhost', port=8080, server=GeventWebSocketServer, debug=True, reloader=True)
