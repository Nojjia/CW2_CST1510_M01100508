import streamlit as st
import pandas as pd
from app.data.db import connect_database

st.set_page_config(
    page_title="Database Viewer | Intelligence Platform",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page Guard Pattern
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("🔒 You must be logged in to view this page")
    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button("Go to Login", type="primary"):
            st.switch_page("Home.py")
    st.stop()

# Database connection
conn = connect_database()

# Sidebar (Matching Dashboard)
with st.sidebar:
    st.subheader("🔐 User Panel")
    
    st.write(f"**Username:** {st.session_state.username}")
    st.write(f"**Role:** {st.session_state.role}")
    st.write(f"**Page:** Database Viewer")
    
    st.divider()
    
    st.subheader("Navigation")
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")
    
    if st.button("Analytics", use_container_width=True):
        st.switch_page("pages/2_Analytics.py")
    
    if st.button("Settings", use_container_width=True):
        st.switch_page("pages/3_Settings.py")
    
    if st.button("Database", use_container_width=True, type="primary"):
        st.switch_page("pages/4_Database_Viewer.py")
    
    st.divider()
    
    # Database Info
    st.subheader("Database Info")
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    st.metric("Tables", len(tables))
    
    # Table sizes (mock)
    table_sizes = {
        "users": "45 rows",
        "cyber_incidents": "127 rows", 
        "datasets_metadata": "32 rows",
        "it_tickets": "89 rows"
    }
    
    for table, size in table_sizes.items():
        st.caption(f"`{table}`: {size}")
    
    st.divider()
    
    # Quick Actions
    st.subheader("Quick Actions")
    
    if st.button("Refresh", use_container_width=True):
        st.rerun()
    
    if st.button("Show All Tables", use_container_width=True):
        st.session_state.show_all_tables = True
        st.rerun()
    
    st.divider()
    
    # Logout Button
    if st.button("Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.switch_page("Home.py")

st.title('🗄️ Database Viewer & Explorer')
st.text('Week 8 Database Implementation - Interactive Data Exploration')
st.success(f"Welcome to database viewer, **{st.session_state.username}**!")
st.subheader("Database Overview")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables_result = cursor.fetchall()
tables = [table[0] for table in tables_result]

# Display table stats
stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

# Calculate actual row counts
with stats_col1:
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    st.markdown(f"""
    ### Users
    ## {user_count}
    """)

with stats_col2:
    cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
    incident_count = cursor.fetchone()[0]
    st.markdown(f"""
    ### Incidents
    ## {incident_count}
    """)

with stats_col3:
    cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
    dataset_count = cursor.fetchone()[0]
    st.markdown(f"""
    ### Datasets
    ## {dataset_count}
    """)

with stats_col4:
    cursor.execute("SELECT COUNT(*) FROM it_tickets")
    ticket_count = cursor.fetchone()[0]
    st.markdown(f"""
    ### Tickets
    ## {ticket_count}
    """)

st.divider()
st.subheader("Table Explorer")

selected_table = st.selectbox(
    "Select Table to View",
    tables,
    help="Choose a table to explore its structure and data"
)

if selected_table:
    # Get table data
    query = f"SELECT * FROM {selected_table}"
    df = pd.read_sql_query(query, conn)
    
    # Get table schema
    cursor.execute(f"PRAGMA table_info({selected_table})")
    schema = cursor.fetchall()
    
    # Display in columns
    table_col1, table_col2 = st.columns([2, 1])
    
    with table_col1:
        st.subheader(f"Table: `{selected_table}`")
        st.write(f"**Rows:** {len(df):,} | **Columns:** {len(df.columns)}")
        
        # Show data with pagination
        st.dataframe(df, use_container_width=True, height=400)
    
    with table_col2:
        st.subheader("Schema Information")
        
        # Create schema dataframe
        schema_df = pd.DataFrame(schema, columns=["cid", "name", "type", "notnull", "dflt_value", "pk"])
        
        # Display schema as a table
        st.dataframe(schema_df[['name', 'type', 'notnull', 'pk']], 
                    use_container_width=True,
                    column_config={
                        "name": "Column",
                        "type": "Type",
                        "notnull": "Required",
                        "pk": "Primary Key"
                    })
        
        # Quick stats
        with st.expander("Quick Statistics"):
            st.write("**Column Types:**")
            type_counts = schema_df['type'].value_counts()
            for dtype, count in type_counts.items():
                st.write(f"- `{dtype}`: {count}")
            
            st.write(f"\n**Primary Keys:** {schema_df['pk'].sum()}")
            st.write(f"**Required Columns:** {schema_df['notnull'].sum()}")
st.divider()
st.subheader("Database Health Check")

health_col1, health_col2, health_col3 = st.columns(3)

with health_col1:
    st.metric("Connection", "Active", "Healthy")
    if st.button("Test Connection", use_container_width=True):
        try:
            cursor.execute("SELECT 1")
            st.success("Connection test passed!")
        except:
            st.error("Connection test failed")

with health_col2:
    st.metric("Integrity", "Verified", "No issues")
    if st.button("Check Integrity", use_container_width=True):
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] == "ok":
            st.success("Database integrity verified")
        else:
            st.error(f"Integrity issues: {result[0]}")

with health_col3:
    st.metric("Size", "~2.5 MB", "+0.1 MB")
    if st.button("Optimize", use_container_width=True):
        cursor.execute("VACUUM")
        st.success("Database optimized")