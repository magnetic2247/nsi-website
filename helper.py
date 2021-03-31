from passlib.hash import bcrypt
import database.db_connection as db
import json

# Users in database
def users(username=None):
    # Looking for specific user
    if username is not None:
        res = db.query("SELECT id,username FROM users WHERE username=?", (username,))
    # Looking for all users
    else:
        res = db.query("SELECT id,username FROM users")

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result[idx] = dict(row) 

    # Return JSON
    return json.dumps(json_result)

# Users in certain chat
def chat_users(id):
    # Query
    res = db.query("SELECT member_id FROM `chat_members` WHERE chat_id=?", (id,))

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result[idx] = dict(row) 

    # Return JSON
    return json.dumps(json_result)

# Chats per user
def chats(username):
    # Query
    res = db.query("SELECT chats.name, chat_members.chat_id FROM chat_members INNER JOIN chats ON chat_members.chat_id=chats.id WHERE chat_members.member_id=(SELECT id FROM `users` WHERE username=?)", (username,))

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result[idx] = dict(row) 

    # Return JSON
    return json.dumps(json_result)

# Messages in chats
def messages(username, password, chat_id, last_msg=False):
    # Attempt login and get user info
    attempt = login(username, password)
    if not attempt[0]:
        return "{}"
    
    # Get User id from user info
    user_id = json.loads(attempt[1])["id"]

    # Check if user in chat
    res = db.query("SELECT * FROM chat_members WHERE member_id=? AND chat_id=?", (user_id, chat_id))
    if res.fetchone() is None:
        return 
    
    # Query
    if not last_msg:
        res = db.query("SELECT messages.chat_id,users.username,messages.content FROM `messages` INNER JOIN `users` ON users.id=messages.sender_id WHERE messages.chat_id=? AND messages.id IN (SELECT id FROM `messages` ORDER BY id DESC LIMIT 100) ORDER BY messages.id", (chat_id,))
    else:
        res = db.query("SELECT * FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT 1", (chat_id,))

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result["msg_"+str(idx)] = dict(row)

    # Return JSON
    return json.dumps(json_result)

# Add user to chat
def add_user_chat(username, password, chatid, user_to_add):
    # Attempt login
    if not login(username, password)[0]:
        return "login_failed"

    # Add user
    db.query("INSERT INTO `chat_members` (chat_id, member_id) VALUES (?, (SELECT id FROM `users` WHERE username=?))", (int(chatid), user_to_add))
    return "ok"

# New Message
def new_message(username, password, message, chat_id):
    # Attempt login and get user info
    attempt = login(username, password)
    if not attempt[0]:
        return "login_failed"
    
    # Get User id from user info
    user_id = json.loads(attempt[1])["id"]

    # Check if user in chat
    res = db.query("SELECT * FROM chat_members WHERE member_id=? AND chat_id=?", (user_id, chat_id))
    if res.fetchone() is None:
        return "{}"

    # Insert new message
    db.query("INSERT INTO `messages` (sender_id, chat_id, content) VALUES (?,?,?)", (user_id, chat_id, message))

    # Send back message to user
    return json.dumps({"chat_id":chat_id,"username":username,"content":message})

# New chat
def new_chat(username, password, name):
    # Attempt login
    if not login(username, password)[0]:
        return "login_failed"

    # Insert new chat into database
    db.query("INSERT INTO `chats` (name) VALUES (?)", (name,))

    # Get new chat id
    chatid = list(dict(db.query("SELECT id FROM `chats` WHERE name=? ORDER BY id DESC", (name,)).fetchone()).values())[0]

    # Add user to new chat
    add_user_chat(username, password, chatid, username)

    return "ok"

# User login
def login(username, password):
    # SQL Query
    query = db.query("SELECT * FROM `users` WHERE username=?", (username,))
    res = query.fetchone()

    # Username Incorrect
    if res is None:
        return (False, "Username or Password incorrect")
    # Password Incorrecy
    if not bcrypt.verify(password, res["password"]):
        return (False, "Username or Password incorrect")
    # All Good!
    else:
        return (True, json.dumps(dict(res)))

# User Register
def register(username, password):
    # Check if username already taken
    if users(username) != "{}":
        return (False, "Username already taken")

    # Hash Password using bcrypt
    hashed_password = bcrypt.hash(password)

    # Register User in Database
    db.query("INSERT INTO users (username, password) VALUES (?,?)", (username, hashed_password))

    # Add user to default chat
    db.query("INSERT INTO `chat_members` VALUES(1,(SELECT id FROM `users` WHERE username=?))", (username,))

    # Return User Info for Login
    query = db.query("SELECT * FROM `users` WHERE username=?", (username,))
    res = query.fetchone()
    return (True, json.dumps(dict(res)))
