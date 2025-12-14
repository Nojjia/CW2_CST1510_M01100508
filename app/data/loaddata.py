import pandas as pd
import sqlite3
from pathlib import Path
def load_csv_to_table_cyber_incident(conn, csv_path, table_name):
    # int: Number of rows loaded
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    df = df.rename(columns={
        "timestamp": "date",
        "category": "incident_type"
    })
    df = df.drop(columns=["incident_id"])
    df["reported_by"] = None
    return df.to_sql(
        name=table_name,
        con=conn,
        if_exists="append",
        index=False
    )

def load_csv_to_table_datasets_metadata(conn, csv_path, table_name):
    """
    Simplified version for loading datasets metadata.
    Assumes CSV has: dataset_id, name, rows, columns, uploaded_by, upload_date
    """
    import pandas as pd
    from pathlib import Path
    
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        print(f"⚠️ File not found: {csv_path}")
        return 0
    
    df = pd.read_csv(csv_path)
    
    # Create a new DataFrame with the exact database schema
    df_db = pd.DataFrame()
    
    # Map CSV columns to database columns
    df_db["dataset_name"] = df["name"]  # CSV 'name' -> DB 'dataset_name'
    df_db["record_count"] = df["rows"]  # CSV 'rows' -> DB 'record_count'
    df_db["source"] = df["uploaded_by"]  # CSV 'uploaded_by' -> DB 'source'
    df_db["last_updated"] = df["upload_date"]  # CSV 'upload_date' -> DB 'last_updated'
    
    # Add calculated/derived columns
    df_db["category"] = "General"  # Default category
    
    # Calculate file_size_mb: (rows × columns × 100 bytes) / (1024×1024)
    df_db["file_size_mb"] = (df["rows"] * df["columns"] * 100) / (1024 * 1024)
    df_db["file_size_mb"] = df_db["file_size_mb"].round(2)
    
    # Insert into database
    rows_loaded = df_db.to_sql(
        name=table_name,
        con=conn,
        if_exists="append",
        index=False
    )
    
    print(f"✅ Loaded {rows_loaded} datasets into {table_name}")
    return rows_loaded

def load_csv_to_table_it_tickets(conn, csv_path, table_name):
    """
    Load IT tickets CSV data into the it_tickets table.
    Handles duplicate ticket_id values by skipping or updating.
    """
    import pandas as pd
    from pathlib import Path
    
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        print(f"⚠️ File not found: {csv_path}")
        return 0
    
    try:
        # Read the CSV
        df = pd.read_csv(csv_path)
        print(f"📄 Read {len(df)} rows from {csv_path.name}")
        
        # Check if CSV has required columns
        required_columns = ["ticket_id", "priority", "description", "status", "assigned_to", "created_at", "resolution_time_hours"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return 0
        
        # Create a copy for processing
        df_processed = df.copy()
        
        # 1. Check for duplicate ticket_id in CSV itself
        csv_duplicates = df_processed[df_processed.duplicated(subset=["ticket_id"], keep=False)]
        if not csv_duplicates.empty:
            print(f"⚠️ Found {len(csv_duplicates)} duplicate ticket_id(s) in CSV, keeping first occurrence")
            df_processed = df_processed.drop_duplicates(subset=["ticket_id"], keep="first")
        
        # 2. Check for existing records in database
        cursor = conn.cursor()
        existing_tickets = []
        
        # Get all existing ticket_ids from database
        cursor.execute("SELECT ticket_id FROM it_tickets")
        existing_tickets = [row[0] for row in cursor.fetchall()]
        
        if existing_tickets:
            # Filter out rows that already exist in database
            before_filter = len(df_processed)
            df_processed = df_processed[~df_processed["ticket_id"].isin(existing_tickets)]
            after_filter = len(df_processed)
            
            duplicates_removed = before_filter - after_filter
            if duplicates_removed > 0:
                print(f"⚠️ Skipped {duplicates_removed} rows that already exist in database")
        
        # If no new rows to insert, return early
        if df_processed.empty:
            print("ℹ️ All rows already exist in database, nothing to insert")
            return 0
        
        # 3. Prepare columns for database schema
        # Map CSV columns to database columns
        df_processed = df_processed.rename(columns={
            "created_at": "created_date"
        })
        
        # Add missing columns with default values
        if "category" not in df_processed.columns:
            # Extract category from first word of description
            df_processed["category"] = df_processed["description"].apply(
                lambda x: x.split()[0] if isinstance(x, str) and x.strip() else "General"
            )
        
        if "subject" not in df_processed.columns:
            # Create subject from description (first 50 chars)
            df_processed["subject"] = df_processed["description"].apply(
                lambda x: (x[:50] + "...") if isinstance(x, str) and len(x) > 50 else x
            )
        
        # Calculate resolved_date from created_date + resolution_time_hours
        if "resolution_time_hours" in df_processed.columns:
            from datetime import datetime, timedelta
            
            def calculate_resolved_date(row):
                try:
                    if pd.isna(row.get("resolution_time_hours")) or row["resolution_time_hours"] == "":
                        return None
                    
                    # Parse created_date
                    created = datetime.strptime(str(row["created_date"]), "%Y-%m-%d")
                    # Add hours
                    resolved = created + timedelta(hours=float(row["resolution_time_hours"]))
                    return resolved.strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Warning: Could not calculate resolved_date for ticket {row.get('ticket_id')}: {e}")
                    return None
            
            df_processed["resolved_date"] = df_processed.apply(calculate_resolved_date, axis=1)
        else:
            df_processed["resolved_date"] = None
        
        # Ensure all database columns exist
        db_columns = [
            "ticket_id", "priority", "status", "category", 
            "subject", "description", "created_date", 
            "resolved_date", "assigned_to"
        ]
        
        # Add any missing columns with None
        for col in db_columns:
            if col not in df_processed.columns:
                df_processed[col] = None
        
        # Reorder columns to match database
        df_processed = df_processed[db_columns]
        
        # 4. Insert data with error handling for each row
        rows_inserted = 0
        cursor = conn.cursor()
        
        for _, row in df_processed.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO it_tickets 
                    (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(row))
                rows_inserted += 1
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint" in str(e):
                    print(f"⚠️ Skipping duplicate ticket_id: {row['ticket_id']}")
                    continue
                else:
                    print(f"❌ Error inserting ticket {row['ticket_id']}: {e}")
            except Exception as e:
                print(f"❌ Error inserting ticket {row['ticket_id']}: {e}")
        
        conn.commit()
        
        print(f"✅ Successfully inserted {rows_inserted} new rows into {table_name} table")
        print(f"📊 Total tickets in database now: {len(existing_tickets) + rows_inserted}")
        
        return rows_inserted
        
    except Exception as e:
        print(f"❌ Error loading CSV to {table_name}: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 0

