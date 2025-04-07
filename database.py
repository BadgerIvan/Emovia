import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('emovia.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              password TEXT NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS moods
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  date DATE NOT NULL,
                  mood TEXT NOT NULL,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  UNIQUE(user_id, date))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  date DATE NOT NULL,
                  content TEXT NOT NULL,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('emovia.db')

def create_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        hashed_pw = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 (username, hashed_pw))
        user_id = c.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user(username, password=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and (password is None or check_password_hash(user[1], password)):
        return user[0]  
    return None

def get_week_moods(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
    
    c.execute('''SELECT date, mood FROM moods 
                 WHERE user_id = ? AND date BETWEEN ? AND ?
                 ORDER BY date''', (user_id, start_date, end_date))
    moods = c.fetchall()
    conn.close()
    
    return {m[0]: m[1] for m in moods}

def record_mood(user_id, date, mood):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO moods (user_id, date, mood)
                 VALUES (?, ?, ?)''', (user_id, date, mood))
    conn.commit()
    conn.close()

def get_moods(user_id, days=10):
    conn = get_db_connection()
    c = conn.cursor()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    c.execute('''SELECT date, mood FROM moods 
                 WHERE user_id = ? AND date BETWEEN ? AND ?
                 ORDER BY date DESC''', (user_id, start_date, end_date))
    moods = c.fetchall()
    conn.close()
    return moods

def get_today_mood(user_id):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT mood FROM moods WHERE user_id = ? AND date = ?", 
              (user_id, today))
    mood = c.fetchone()
    conn.close()
    return mood[0] if mood else None

def create_note(user_id, date, content):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, date, content) VALUES (?, ?, ?)",
             (user_id, date, content))
    conn.commit()
    note_id = c.lastrowid
    conn.close()
    return note_id

def get_notes(user_id, date=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    if date:
        c.execute("SELECT id, date, content FROM notes WHERE user_id = ? AND date = ? ORDER BY date DESC", 
                 (user_id, date))
    else:
        c.execute("SELECT id, date, content FROM notes WHERE user_id = ? ORDER BY date DESC", 
                 (user_id,))
    
    notes = c.fetchall()
    conn.close()
    return [{"id": n[0], "date": n[1], "content": n[2]} for n in notes]

def delete_note(note_id, user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    conn.commit()
    affected_rows = c.rowcount
    conn.close()
    return affected_rows > 0