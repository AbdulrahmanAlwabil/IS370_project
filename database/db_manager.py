import sqlite3
import bcrypt

DB_PATH = 'database\chat.db'

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
        
        # If the user exists, verify the password
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

# ========================
#    GROUP MANAGEMENT
# ========================

def create_group(group_name):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
        print(f"Group '{group_name}' created.")
    except sqlite3.IntegrityError:
        print(f"Group '{group_name}' already exists.")

def get_group_id(group_name):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        row = cur.fetchone()
        return row[0] if row else None

def add_user_to_group(username, group_name):
    user_id = get_user_id(username)
    group_id = get_group_id(group_name)

    if user_id and group_id:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT INTO group_members (user_id, group_id) VALUES (?, ?)", (user_id, group_id))
            print(f"Added '{username}' to group '{group_name}'.")
        except sqlite3.IntegrityError:
            print(f"User '{username}' is already in group '{group_name}'.")
    else:
        print("Invalid username or group name.")

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

# ========================
# MESSAGES
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

# ========================
# MAIN FOR TESTING
# ========================

if __name__ == "__main__":
    init_db()

    # create_user('alice', '1234')
    # create_group('team')
    # add_user_to_group('alice', 'team')
    # create_message('alice', 'team', 'multicast', 'Hello Team!')
