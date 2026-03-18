import sqlite3
from datetime import datetime

DATABASE = "bot.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'ru'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            destination TEXT NOT NULL,
            people_count INTEGER NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            channel_message_id INTEGER,
            lang TEXT DEFAULT 'ru',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    conn.commit()
    conn.close()


def create_order(user_id, name, phone, destination, people_count, time, lang='ru'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, name, phone, destination, people_count, time, status, lang)
        VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (user_id, name, phone, destination, people_count, time, lang))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id


def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_pending_orders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_order_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status IN ('accepted', 'rejected') ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_order_status(order_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def set_channel_message_id(order_id, channel_message_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET channel_message_id = ? WHERE id = ?", (channel_message_id, order_id))
    conn.commit()
    conn.close()


def has_pending_order(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders WHERE user_id = ? AND status = 'pending'", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def delete_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()


def get_user_lang(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row['lang'] if row else 'ru'


def set_user_lang(user_id, lang):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, lang) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET lang = ?
    """, (user_id, lang, lang))
    conn.commit()
    conn.close()


def add_package(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO packages (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_packages():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM packages ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_package(package_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM packages WHERE id = ?", (package_id,))
    conn.commit()
    conn.close()


def get_orders_by_status(status, limit=10, offset=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?
    """, (status, limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_orders_count_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = ?", (status,))
    row = cursor.fetchone()
    conn.close()
    return row['count'] if row else 0
