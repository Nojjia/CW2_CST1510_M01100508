import pandas as pd
from app.data.db import connect_database
def insert_datasets_metadata(conn, dataset_name, category, source, last_updated, record_count, file_size_mb):
    # Insert new incident
    cursor = conn.cursor()
    insert_dataset_metadata_sql = """
    INSERT INTO datasets_metadata (
        dataset_name,
        category,
        source,
        last_updated,
        record_count,
        file_size_mb
    ) VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_dataset_metadata_sql, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    return cursor.lastrowid

def get_all_datasets_metadata(conn):
    # Get all incidents as DataFrame
    select_data_sql = """
    SELECT *
    FROM datasets_metadata
    ORDER BY id DESC
    """
    return pd.read_sql_query(select_data_sql, conn)