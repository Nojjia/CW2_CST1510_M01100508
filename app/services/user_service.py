import bcrypt
import sqlite3
from pathlib import Path
from app.data.db import DATA_DIR
from app.data.users import get_user_by_username, insert_user

def register_user(conn, username, password, role="user"):
    """Register new user with password hashing."""
    cursor = conn.cursor()

    # Find user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return False, f"Username '{username}' already exists."
    
    password_encoded = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_encoded = bcrypt.hashpw(password_encoded, salt)
    hashed = hashed_encoded.decode('utf-8')
    
    insert_user(conn, username, hashed, role)
    conn.commit()

    return True, f"User '{username}' registered successfully."


def login_user(conn, username, password):
    """Authenticate user."""
    cursor = conn.cursor()

    user = get_user_by_username(conn, username)
    if not user:
        return False, "Username not found."
    
    # Verify password (user[2] is password_hash column)
    hashed = user[2]
    password_encoded = password.encode('utf-8')
    hash_bytes = hashed.encode('utf-8')
    
    if bcrypt.checkpw(password_encoded, hash_bytes):
        return True, user[3]
    else:
        return False, "Incorrect password."

def migrate_users_from_file(conn, filepath=DATA_DIR / "users.txt"):
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   No users to migrate.")
        return

    cursor = conn.cursor()
    migrated_count = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                hashed = parts[1]
                role = parts[2]
                try:
                    insert_user(conn, username, hashed, role)
                    conn.commit()
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")
