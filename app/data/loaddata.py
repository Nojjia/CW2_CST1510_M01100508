import pandas as pd
from pathlib import Path
def load_csv_to_table_cyber_incident(conn, csv_path, table_name):
    # int: Number of rows loaded
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
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
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
        return 0
    
    try:
        # Read the CSV
        df = pd.read_csv(csv_path)
        print(f"📄 Read {len(df)} rows from {csv_path.name}")
        
        # Different column mappings for different tables
        if table_name == "cyber_incidents":
            # For cyber incidents CSV
            df = df.rename(columns={
                "timestamp": "date",
                "category": "incident_type"
            })
            # Add missing columns if needed
            if "reported_by" not in df.columns:
                df["reported_by"] = None
            if "incident_id" in df.columns:
                df = df.drop(columns=["incident_id"])
                
        elif table_name == "datasets_metadata":
            # For datasets metadata CSV (your sample data)
            df = df.rename(columns={
                "dataset_id": "id",  # If you want to use auto-increment, omit this
                "name": "dataset_name",
                "rows": "record_count",
                "uploaded_by": "source",  # Adjust based on your schema
                "upload_date": "last_updated"
            })
            
            # Add missing columns from your schema
            if "category" not in df.columns:
                df["category"] = "General"  # Default category
            
            if "file_size_mb" not in df.columns:
                # Calculate approximate file size (assume ~100 bytes per row)
                df["file_size_mb"] = df["record_count"] * 100 / (1024 * 1024)
                df["file_size_mb"] = df["file_size_mb"].round(2)
            
            # Ensure columns match your schema
            expected_columns = ["dataset_name", "category", "source", "last_updated", 
                              "record_count", "file_size_mb"]
            
            # Keep only columns that exist in the CSV
            df = df[[col for col in expected_columns if col in df.columns]]
            
        elif table_name == "it_tickets":
            # For IT tickets CSV (if needed)
            if "ticket_id" not in df.columns:
                # Generate ticket IDs if missing
                df["ticket_id"] = ["IT-" + str(1000 + i) for i in range(len(df))]
        
        # Load into database
        rows_loaded = df.to_sql(
            name=table_name,
            con=conn,
            if_exists="append",
            index=False
        )
        
        print(f"✅ Successfully loaded {rows_loaded} rows into {table_name} table")
        return rows_loaded
        
    except Exception as e:
        print(f"❌ Error loading CSV to {table_name}: {e}")
        return 0
    
def load_csv_to_table_it_tickets(conn, csv_path, table_name):
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
        return 0
    
    try:
        # Read the CSV
        df = pd.read_csv(csv_path)
        print(f"📄 Read {len(df)} rows from {csv_path.name}")
        
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Handle missing columns and rename if needed
        # Map CSV columns to database columns
        column_mapping = {
            "ticket_id": "ticket_id",  # CSV -> DB
            "priority": "priority",
            "description": "description",
            "status": "status",
            "assigned_to": "assigned_to",
            "created_at": "created_date",  # created_at -> created_date
            "resolution_time_hours": "resolved_date"  # We'll convert this
        }
        
        # Rename columns based on mapping
        for csv_col, db_col in column_mapping.items():
            if csv_col in df_processed.columns:
                df_processed = df_processed.rename(columns={csv_col: db_col})
        
        # Check required columns
        required_columns = ["ticket_id", "subject"]
        for col in required_columns:
            if col not in df_processed.columns:
                print(f"❌ Missing required column: {col}")
                return 0
        
        # Handle missing columns from schema
        # 1. category - create from description or set default
        if "category" not in df_processed.columns:
            if "description" in df_processed.columns:
                # Extract category from first few words of description
                df_processed["category"] = df_processed["description"].apply(
                    lambda x: x.split()[0] if isinstance(x, str) and x.strip() else "General"
                )
            else:
                df_processed["category"] = "General"
        
        # 2. subject - if not in CSV, create from description
        if "subject" not in df_processed.columns:
            if "description" in df_processed.columns:
                df_processed["subject"] = df_processed["description"].apply(
                    lambda x: (x[:50] + "...") if isinstance(x, str) and len(x) > 50 else x
                )
            else:
                df_processed["subject"] = "IT Support Ticket"
        
        # 3. created_date - if not in CSV, use current timestamp
        if "created_date" not in df_processed.columns:
            from datetime import datetime
            df_processed["created_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # 4. resolved_date - calculate from created_date + resolution_time_hours
        if "resolved_date" not in df_processed.columns:
            if "resolution_time_hours" in df.columns:
                # Convert resolution_time_hours to resolved_date
                from datetime import datetime, timedelta
                
                def calculate_resolved_date(created_date_str, hours):
                    try:
                        if pd.isna(hours) or hours == "":
                            return None
                        created_date = datetime.strptime(created_date_str, "%Y-%m-%d")
                        resolved_date = created_date + timedelta(hours=float(hours))
                        return resolved_date.strftime("%Y-%m-%d")
                    except:
                        return None
                
                # Check if we have created_date column
                if "created_date" in df_processed.columns:
                    df_processed["resolved_date"] = df_processed.apply(
                        lambda row: calculate_resolved_date(row["created_date"], row.get("resolution_time_hours")),
                        axis=1
                    )
                else:
                    df_processed["resolved_date"] = None
            else:
                df_processed["resolved_date"] = None
        
        # Ensure all database columns exist in the DataFrame
        db_columns = [
            "ticket_id", "priority", "status", "category", 
            "subject", "description", "created_date", 
            "resolved_date", "assigned_to"
        ]
        
        # Add any missing columns with None values
        for col in db_columns:
            if col not in df_processed.columns:
                df_processed[col] = None
        
        # Reorder columns to match database schema order
        df_processed = df_processed[db_columns]
        
        # Remove duplicate ticket_ids before inserting
        duplicates = df_processed[df_processed.duplicated(subset=["ticket_id"], keep=False)]
        if not duplicates.empty:
            print(f"⚠️  Found {len(duplicates)} duplicate ticket_id(s), keeping first occurrence")
            df_processed = df_processed.drop_duplicates(subset=["ticket_id"], keep="first")
        
        # Load into database
        rows_loaded = df_processed.to_sql(
            name=table_name,
            con=conn,
            if_exists="append",
            index=False
        )
        
        print(f"✅ Successfully loaded {rows_loaded} rows into {table_name} table")
        return rows_loaded
        
    except Exception as e:
        print(f"❌ Error loading CSV to {table_name}: {e}")
        import traceback
        traceback.print_exc()
        return 0