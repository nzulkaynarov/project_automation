import sqlite3
import logging

DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            image TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def get_all_product_ids():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products")
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

def add_product(product):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (id, title, description, image) VALUES (?, ?, ?, ?)",
            (product['id'], product['title'], product['description'], product['image'])
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already exists
    finally:
        conn.close()

def add_user(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def get_products(limit=1, offset=0):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, image FROM products LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [{'id': r[0], 'title': r[1], 'description': r[2], 'image': r[3]} for r in rows]

def get_products_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def search_products(query, limit=1, offset=0):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute("SELECT id, title, description, image FROM products WHERE title LIKE ? OR description LIKE ? LIMIT ? OFFSET ?", (search_term, search_term, limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [{'id': r[0], 'title': r[1], 'description': r[2], 'image': r[3]} for r in rows]

def get_search_count(query):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute("SELECT COUNT(*) FROM products WHERE title LIKE ? OR description LIKE ?", (search_term, search_term))
    count = cursor.fetchone()[0]
    conn.close()
    return count
