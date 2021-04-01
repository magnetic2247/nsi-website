import bottle_session, bottle
from bottle import route, template, run, request, response, static_file, get, post, redirect
from bottle.ext.websocket import GeventWebSocketServer, websocket
import helper as h
import json

# Bottle App with Session plugin
app = bottle.app()
plugin = bottle_session.SessionPlugin(cookie_lifetime=600, cookie_secure=True)
app.install(plugin)

# Index
@route('/')
def index():
    return template("frontend/index.html")

# About page
@route('/about')
def about():
    return template("frontend/about/index.html")

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
        # Login User
        else:
            data = h.login(login, passwd)
            if data[0]:
                session['id'] = json.loads(data[1])["id"]
                session['username'] = login
                session['password'] = passwd
                return redirect('/chat')
            else:
                redirect("/login?error")
    else:
        return redirect("/")

# API
# Check if username taken
@route('/api/username/<user>')
def api_check_user(user):
    if h.users(user) == "{}":
        return "ok"
    return "taken"
# Get info about specific user
@route('/api/user/<user>')
def api_specific_user(user):
    info = h.users(user)
    if info != "{}":
        return json.dumps(json.loads(info)["0"])
# Get all the chats a specific user if in
@route('/api/chats/<user>')
def api_chats_specific_user(user):
    return h.chats(user)
# Get all users if a specific chat
@route('/api/chat_users/<id>')
def api_users_specific_chat(id):
    return h.chat_users(id)
# Get All users
@route('/api/users')
def api_all_users():
    return h.users()
# Get username if logged-in
@route('/api/logged-in')
def api_logged_in(session):
    if 'id' in session and 'username' in session and 'password' in session:
        return session['username']
    else:
        return "not_logged_in"
# Add user to chat
@route('/api/add-user-chat/<user>/<chatid>')
def api_add_user_chat(session, user, chatid):
    if 'id' in session and 'username' in session and 'password' in session:
        return h.add_user_chat(session['username'], session['password'], chatid, user)
# Create chat
@route('/api/create-chat/<name>')
def api_create_chat(session, name):
    if 'id' in session and 'username' in session and 'password' in session:
        return h.new_chat(session['username'], session['password'], name)

# Static Files
@route('/<filename:path>')
def static_index(filename):
    response.set_header('If-Modified-Since', 'Wed, 21 Oct 2015 07:28:00 GMT')
    response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate, public, max-age=0')
    return static_file(filename, root='frontend/')

# Web Sockets
users = set()
@route('/socket', apply=[websocket])
def wsocket(ws, session):
    try:
        # New Client
        # Check if user logged in
        if 'id' in session and 'username' in session and 'password' in session:
            users.add((ws,int(session['id'])))
        else:
            ws.send("not_logged_in")

        # Keep Connection Alive
        while True:
            # Receive Message
            msg = ws.receive()

            # Check if client still connected
            if msg is not None:
                # Check if user still logged in
                if 'id' in session and 'username' in session and 'password' in session:
                    # User requests all messages
                    if msg == "all":
                        # Load all chats for particular user
                        all_chats = json.loads(h.chats(session['username']))

                        # Go through all chats
                        for v in all_chats.values():
                            # Load all messages for certain chat
                            all_messages = json.loads(h.messages(session['username'],session['password'],v['chat_id']))

                            # Send messages
                            for v in all_messages.values():
                                ws.send(json.dumps(v))
                    # User sent regular message
                    else:
                        # Send message and get it from db
                        chatid = json.loads(msg)['chat_id']
                        message = json.loads(msg)['content']
                        db_message = h.new_message(session['username'],session['password'],message,chatid)

                        # Check if message was successfully sent
                        if db_message != "{}":
                            # Get ids of all users in chat
                            db_userids = h.chat_users(chatid)
                            userids=[]
                            for v in json.loads(db_userids).values():
                                userids.append(v['member_id'])

                            # Send message back to sender
                            ws.send(db_message)

                            # Send message to all connected users in this chat
                            for user in users:
                                if user[1] in userids and user[0] != ws:
                                    user[0].send(db_message)

                else:
                    ws.send("session_expired")

            # Client Disconnected
            else:
                break
        # Remove Disconnected Client
        users.remove((ws,int(session['id'])))
    # Error! Print Error
    except Exception as e:
        print("Error:", e)

# Start server
if os.environ.get('APP_LOCATION') == 'heroku':
    run(host="0.0.0.0", port=os.environ.get("PORT", 5000), server=GeventWebSocketServer)
else:
    run(app=app, server=GeventWebSocketServer, host='0.0.0.0', port=8080)
