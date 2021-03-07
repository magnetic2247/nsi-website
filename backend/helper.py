import backend.db_connection as db
import json

# Users in database
def users(id=None):
    # Looking for specific user
    if id is not None:
        res = db.query("SELECT * FROM users WHERE id=?", (id,))
    # Looking for all users
    else:
        res = db.query("SELECT * FROM users")

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result[idx] = dict(row) 

    # Return JSON
    return json.dumps(json_result)

# Users in database
def chats(id):
    # Query
    res = db.query("SELECT chats.name, chat_members.chat_id FROM chat_members INNER JOIN chats ON chat_members.chat_id=chats.id WHERE chat_members.member_id=?", (id,))

    # Convert Results to JSON
    json_result = {}
    for idx,row in enumerate(res):
        json_result[idx] = dict(row) 

    # Return JSON
    return json.dumps(json_result)

# Message in chats
def messages(user_id, chat_id, last_msg=False):
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
