import pandas as pd
from app.data.db import connect_database
def insert_ticket(conn, priority, status, category, subject, description, created_date, resolved_date, assigned_to):
    # Insert new incident
    cursor = conn.cursor()
    insert_dataset_metadata_sql = """
    INSERT INTO it_tickets (
        priority,
        status,
        category,
        subject,
        description,
        created_date,
        resolved_date,
        assigned_to
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_dataset_metadata_sql, (priority, status, category, subject, description, created_date, resolved_date, assigned_to))
    return cursor.lastrowid

def get_all_tickets(conn):
    # Get all incidents as DataFrame
    select_data_sql = """
    SELECT *
    FROM it_tickets
    ORDER BY created_at DESC
    """
    return pd.read_sql_query(select_data_sql, conn)