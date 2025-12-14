from app.data.db import connect_database
def insert_user(conn, username, password_hash, role='user'):
    # Insert new user
    cursor = conn.cursor()
    insert_data_sql = """
    INSERT INTO users (
        username,
        password_hash,
        role
    ) VALUES (?, ?, ?)
    """
    cursor.execute(insert_data_sql, (username, password_hash, role))
    return cursor.lastrowid

def get_user_by_username(conn, username):
    # Retrieve user by username.
    cursor = conn.cursor()
    query = """
    SELECT *
    FROM users
    WHERE username = ?
    """
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    return user