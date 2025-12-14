import pandas as pd
from app.data.db import connect_database

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    # Insert new incident
    cursor = conn.cursor()
    insert_data_sql = """
    INSERT INTO cyber_incidents (
        date,
        incident_type,
        severity,
        status,
        description,
        reported_by
    ) VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_data_sql, (date, incident_type, severity, status, description, reported_by))
    return cursor.lastrowid

def get_all_incidents(conn):
    # Get all incidents as DataFrame
    select_data_sql = """
    SELECT *
    FROM cyber_incidents
    ORDER BY id DESC
    """
    return pd.read_sql_query(select_data_sql, conn)

def update_incident_status(conn, incident_id, new_status):
    cursor = conn.cursor()
    update_data_sql = """
    UPDATE cyber_incidents
    SET status = ?
    WHERE id = ?"""
    cursor.execute(update_data_sql, (new_status, incident_id))
    return cursor.rowcount

def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    
    TODO: Implement DELETE operation.
    """
    # TODO: Write DELETE SQL: DELETE FROM cyber_incidents WHERE id = ?
    cursor = conn.cursor()
    delete_data_sql = """
    DELETE FROM cyber_incidents
    WHERE id = ?;
    """
    cursor.execute(delete_data_sql, (incident_id,))
    return cursor.rowcount

def get_incidents_by_type_count(conn):
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_severity_by_status(conn):
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incident_types_with_many_cases(conn, min_count=5):
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df