import streamlit as st
import pandas as pd
from app.data.db import connect_database
from app.data.users import get_user_by_username
from app.data.incidents import get_all_incidents, get_high_severity_by_status, get_incidents_by_type_count
from app.data.datasets import get_all_datasets_metadata
from app.data.tickets import get_all_tickets
from app.data.db import DB_PATH, DATA_DIR

st.set_page_config(
    page_title="Dashboard | Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("You must be logged in to view this page")
    if st.button("Go to Login", type="primary"):
        st.switch_page("Home.py")
    st.stop()

conn = connect_database()

st.title('Dashboard')
st.header("Domain-Specific Visuals")
with st.sidebar:
    st.subheader("User Panel")
    
    st.write(f"**Username:** {st.session_state.username}")
    st.write(f"**Role:** {st.session_state.role}")
    st.write(f"**Session:** Active")
    
    st.divider()
    
    st.subheader("Navigatiun")
    if st.button("Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Dashboard.py")
    
    if st.button("Analytics", use_container_width=True):
        st.switch_page("pages/2_Analytics.py")
    
    if st.button("Settings", use_container_width=True):
        st.switch_page("pages/3_Settings.py")
    
    if st.button("View Database", use_container_width=True):
        st.switch_page("pages/4_Database_Viewer.py")

    if st.button("AI Assistant", use_container_width=True):
        st.switch_page("pages/3_AI_Chat.py")
    
    st.divider()
    
    # Quick Actions
    st.subheader("Quick Actions")
    
    if st.button("Refresh Data", use_container_width=True):
        st.rerun()
    
    if st.button("Export Report", use_container_width=True):
        st.info("Report export would be implemented here")
    
    st.divider()
    
    # Logout Button (anchored at bottom)
    if st.button("Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.switch_page("Home.py")

st.text('Comprehensive Overview of All Domains')

st.success(f"✅ Welcome back, **{st.session_state.username}**! You are logged in as **{st.session_state.role}**.")

# --- Fetch Data (Week 8 Functions) ---
# Cybersecurity Data
incidents_df = get_all_incidents(conn)
high_sev_status_df = get_high_severity_by_status(conn)
incidents_by_type = get_incidents_by_type_count(conn)

# Data Science Data
datasets_df = get_all_datasets_metadata(conn)
total_datasets = len(datasets_df)
total_records = datasets_df['record_count'].sum() if not datasets_df.empty else 0
total_size_mb = datasets_df['file_size_mb'].sum() if not datasets_df.empty else 0

# IT Operations Data
tickets_df = get_all_tickets(conn)
open_tickets = len(tickets_df[tickets_df['status'] != 'Resolved']) if not tickets_df.empty else 0
high_priority_tickets = len(tickets_df[tickets_df['priority'] == 'High']) if 'priority' in tickets_df.columns and not tickets_df.empty else 0

# --- KPI Metrics (From Workshop Slide 15) ---
st.subheader("📈 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)


# Replace mardown with
with col1:
    st.markdown(f"""
        ### Security Incidents
        ## {len(incidents_df)}
    """)

with col2:
    st.markdown(f"""
        ### Datasets
        ## {total_datasets}
    """)

with col3:
    st.markdown(f"""
        ### Open Tickets
        ## {open_tickets}
    """)

with col4:
    high_sev_count = high_sev_status_df['count'].sum() if not high_sev_status_df.empty else 0
    st.markdown(f"""
        ### High Severity
        ## {high_sev_count}
    """)

st.divider()
st.divider()

with st.container():
    st.subheader('Cybersecurity Dashboard')
    
    cyber_col1, cyber_col2 = st.columns(2)
    
    with cyber_col1:
        st.subheader("Incident Types")
        if not incidents_by_type.empty:
            chart_data = incidents_by_type.set_index('incident_type')['count']
            st.bar_chart(chart_data)
        else:
            st.info("No incident data available")
    
    with cyber_col2:
        st.subheader("Recent Incidents")
        if not incidents_df.empty:
            st.dataframe(
                incidents_df.head(8),
                use_container_width=True,
                column_config={
                    "id": "ID",
                    "date": "Date",
                    "incident_type": "Type",
                    "severity": "Severity",
                    "status": "Status"
                }
            )
        else:
            st.info("No recent incidents")
    
    # Quick Actions for looking pretty
    with st.expander("⚡ Cybersecurity Actions"):
        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            if st.button("Report Incident", key="report_incident"):
                st.info("To implement later")
        with action_col2:
            if st.button("View All Incidents", key="view_all_incidents"):
                st.info("To implement later")
        with action_col3:
            if st.button("Generate Security Report", key="gen_security_report"):
                st.info("To implement later")

# Data Science Section
st.divider()
with st.container():
    st.subheader("Data Science Dashboard")
    
    data_col1, data_col2 = st.columns(2)
    
    with data_col1:
        st.subheader("Dataset Overview")
        st.info("TO IMPLEMENT LATER")
    
    with data_col2:
        st.subheader("Recent Datasets")
        st.info("TO IMPLEMENT LATER")

with st.container():
    st.subheader('IT Operations Dashboard')
    
    it_col1, it_col2 = st.columns(2)
    
    with it_col1:
        st.subheader("Ticket Status")
        st.info("TO IMPLEMENT LATER")
    
    with it_col2:
        st.subheader("Recent Tickets")
        st.info("TO IMPLEMENT LATER")

# Recet Activity Timeline
st.divider()
st.subheader("Recent Platform Activity")

activity_data = {
    "Time": ["10:30", "11:15", "12:45", "14:20", "15:00"],
    "Activity": ["User 'admin' logged in", "New phishing incident reported", 
                 "Dataset 'sales_q3' uploaded", "Ticket #IT-457 assigned", 
                 "Security scan completed"],
    "Domain": ["System", "Cybersecurity", "Data Science", "IT Operations", "Cybersecurity"]
}

activity_df = pd.DataFrame(activity_data)
st.dataframe(activity_df, use_container_width=True, hide_index=True)
st.write()