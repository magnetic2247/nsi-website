from passlib.hash import bcrypt
import backend.db_connection as db
import json

# Users in database
def users(usrname=None):
    # Looking for specific user
    if usrname is not None:
        res = db.query("SELECT * FROM users WHERE username=?", (usrname,))
    # Looking for all users
    else:
        res = db.query("SELECT * FROM users")

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result[idx] = dict(row) 

    # Return JSON
    return json.dumps(json_result)

# Chats per member
def chats(id):
    # Query
    res = db.query("SELECT chats.name, chat_members.chat_id FROM chat_members INNER JOIN chats ON chat_members.chat_id=chats.id WHERE chat_members.member_id=?", (id,))

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
        res = db.query("SELECT content FROM messages WHERE chat_id=? AND id IN (SELECT id FROM messages ORDER BY id DESC LIMIT 100) ORDER BY id", (chat_id,))
    else:
        res = db.query("SELECT content FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT 1", (chat_id,))

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result[idx] = dict(row)

    # Return JSON
    return json.dumps(json_result)

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
