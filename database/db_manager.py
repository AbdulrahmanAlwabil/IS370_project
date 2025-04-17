import sqlite3
import bcrypt
import os

DB_PATH = os.path.join('database', 'chat.db')

# ========================
# DATABASE INITIALIZATION
# ========================

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Groups table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Group membership table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(group_id) REFERENCES groups(id),
                UNIQUE(user_id, group_id)
            )
        ''')

        # Messages table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER,
                type TEXT CHECK(type IN ('unicast', 'multicast', 'broadcast')) NOT NULL,
                message TEXT NOT NULL,
                attactment BLOB,
                FOREIGN KEY(sender_id) REFERENCES users(id)
            )
        ''')

    print("Database initialized.")

# ========================
# USER MANAGEMENT
# ========================

def create_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        return f"User '{username}' registered"
    except sqlite3.IntegrityError:
        return f"Username '{username}' already exists"

def authenticate_user(username, password):
   
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        
        if row:
            stored_hash = row[0]
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        else:
            # User does not exist
            return False

def get_user_id(username):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return row[0] if row else None

def get_username(id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = ?", (id,))
        row = cur.fetchone()
        return row[0] if row else None
    
# ========================
#    GROUP MANAGEMENT
# ========================

def create_group(group_name):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
        print(f"Group '{group_name}' created.")
        return True
    except sqlite3.IntegrityError:
        print(f"Group '{group_name}' already exists.")
        return False

def add_user_to_group(username, group_name):
    user_id = get_user_id(username)
    group_id = get_group_id(group_name)

    if user_id and group_id:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT INTO group_members (user_id, group_id) VALUES (?, ?)", (user_id, group_id))
            print(f"Added '{username}' to group '{group_name}'.")
            return True
        except sqlite3.IntegrityError:
            print(f"User '{username}' is already in group '{group_name}'.")
            return True  
    else:
        print("Invalid username or group name.")
        return False

def get_group_id(group_name):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        row = cur.fetchone()
        return row[0] if row else None

def get_group_members(group_name):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT u.username FROM users u
            JOIN group_members gm ON u.id = gm.user_id
            JOIN groups g ON g.id = gm.group_id
            WHERE g.name = ?
        ''', (group_name,))
        return [row[0] for row in cur.fetchall()]
    
def get_user_groups(username):
    user_id = get_user_id(username)
    if not user_id:
        return []
        
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT g.name FROM groups AS g
            JOIN group_members AS gm ON gm.group_id = g.id
            WHERE gm.user_id = ?
            ORDER BY g.name ASC
        ''', (user_id,))
        return [row[0] for row in cur.fetchall()]

# ========================
#        MESSAGES
# ========================

def create_message(sender_username, receiver_identifier, msg_type, content):
    sender_id = get_user_id(sender_username)
    receiver_id = None

    if not sender_id:
        return "Query failed: Sender not found."
        

    if msg_type == 'unicast':
        receiver_id = get_user_id(receiver_identifier)
        if not receiver_id:
            return "Unicast failed: user does not exist"
            
    elif msg_type == 'multicast':
        receiver_id = get_group_id(receiver_identifier)
        if not receiver_id:
            return "Multicast failed: group does not exist."
            
    elif msg_type == 'broadcast':
        receiver_id = None
    else:
        return "Record insertion failed: Invalid message type."

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO messages (sender_id, receiver_id, type, message)
            VALUES (?, ?, ?, ?)
        ''', (sender_id, receiver_id, msg_type, content))

    print(f"{msg_type.capitalize()} message stored.")
    
def get_chat_history(sender_name, receiver_name, chat_type):
    sender_id = get_user_id(sender_name)
    
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        history = []
        
        if chat_type == 'broadcast':
            cur.execute('''SELECT message, sender_id FROM messages 
                           WHERE type = 'broadcast'  
                           ORDER BY id ASC''')
            
            for row in cur.fetchall():
                message = row[0]
                sender = get_username(row[1])
                history.append({sender: message})
            
        elif chat_type == 'multicast':
            group_id = get_group_id(receiver_name)
            
            if not group_id:
                print(f"Group '{receiver_name}' not found")
                return []
                
            cur.execute('''SELECT message, sender_id FROM messages 
                           WHERE receiver_id = ? AND type = 'multicast'  
                           ORDER BY id ASC''', (group_id,))
            
            for row in cur.fetchall():
                message = row[0]
                sender = get_username(row[1])
                history.append({sender: message})
                
        elif chat_type == 'unicast':
            receiver_id = get_user_id(receiver_name)
            if not receiver_id:
                return []
                
            cur.execute('''SELECT message, sender_id FROM messages 
                           WHERE ((sender_id = ? AND receiver_id = ?) OR 
                                 (sender_id = ? AND receiver_id = ?)) AND type = 'unicast'  
                           ORDER BY id ASC''', 
                        (sender_id, receiver_id, receiver_id, sender_id))
            
            for row in cur.fetchall():
                message = row[0]
                sender = get_username(row[1])
                history.append({sender: message})
        else:
            raise ValueError('Message type value is not recognized by database (unicast, multicast, broadcast).')
        
        return history

def get_contacts(sender_username):
        
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''SELECT username FROM users 
                        WHERE username != ?   
                        ORDER BY id ASC''', (sender_username,))
        
        return [row[0] for row in cur.fetchall()]

# ========================
# MAIN FOR TESTING
# ========================
    
if __name__ == "__main__":
    init_db()
    
    # get_contacts('abdulrahman')
    # create_user('alice', '1234')
    # create_group('team')
    # add_user_to_group('alice', 'team')
    # create_message('abdulrahman', 'omar', 'unicast', 'Omar, you forgot your phone with me')
    # create_message('mohamed', None, 'broadcast', 'Hey guys, I wanted to invite you all to the party next Friday!')