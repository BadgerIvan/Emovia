import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('emovia.db')
    c = conn.cursor()
    
    # Создаем таблицу пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Создаем таблицу настроений
    c.execute('''CREATE TABLE IF NOT EXISTS moods
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  date DATE NOT NULL,
                  mood TEXT NOT NULL,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  UNIQUE(user_id, date))''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('emovia.db')

def create_user(username):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        user_id = c.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Пользователь уже существует
    finally:
        conn.close()

def get_user(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def record_mood(user_id, date, mood):
    conn = get_db_connection()
    c = conn.cursor()
    # Вставляем или обновляем запись о настроении
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