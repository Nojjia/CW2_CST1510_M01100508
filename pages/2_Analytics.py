import streamlit as st
import pandas as pd
from app.data.db import connect_database
from app.data.incidents import get_incidents_by_type_count, get_high_severity_by_status

st.set_page_config(
    page_title="Analytics | Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("You must be logged in to view this page")
    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button("Go to Login", type="primary"):
            st.switch_page("Home.py")
    st.stop()

# database connection
conn = connect_database()
# Sidebar (Matching Dashboard)
with st.sidebar:
    st.subheader("User Panel")
    st.write(f"**Username:** {st.session_state.username}")
    st.write(f"**Role:** {st.session_state.role}")
    st.write(f"**Page:** Analytics")
    
    st.divider()
    
    st.subheader("📋 Navigation")
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")
    
    if st.button("📈 Analytics", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Analytics.py")
    
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/3_Settings.py")
    
    if st.button("🗄️ Database", use_container_width=True):
        st.switch_page("pages/4_Database_Viewer.py")
    if st.button("AI Assistant", use_container_width=True):
        st.switch_page("pages/3_AI_Chat.py")
    
    st.divider()
    
    # Analytics Filters
    st.subheader("Filters")
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Cybersecurity", "Data Science", "IT Operations", "All Domains"]
    )
    
    # Logout Button
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.switch_page("Home.py")

st.title('Analytics')
incidents_by_type = get_incidents_by_type_count(conn)
high_sev = get_high_severity_by_status(conn)

st.subheader("🔒 Cybersecurity Analysis")
cyber_col1, cyber_col2 = st.columns(2)
with cyber_col1:
    st.subheader("Incident Type Distribution")
    if not incidents_by_type.empty:
        chart_data = incidents_by_type.set_index('incident_type')
        st.bar_chart(chart_data['count'])
with cyber_col2:
    st.subheader("High Severity Analysis")
    if not high_sev.empty:
        chart_data = high_sev.set_index('status')
        st.bar_chart(chart_data['count'])

st.divider()
st.subheader("🎯 Phishing Surge Analysis")


trend_hardcoded= pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Phishing Cases': [12, 15, 22, 35, 42, 38],
    'Resolution Rate %': [85, 82, 78, 65, 58, 62]
})

trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    st.subheader("Phishing Cases Over Time")
    st.line_chart(trend_hardcoded.set_index('Month')['Phishing Cases'])

with trend_col2:
    st.subheader("Resolution Rate Trend")
    st.line_chart(trend_hardcoded.set_index('Month')['Resolution Rate %'])


st.divider()
st.subheader("🖥️ IT Operations Analysis")

st.write("**Problem Statement:** Slow resolution times and staff performance anomalies")

# Simulated staff performance
performance_data = pd.DataFrame({
    'Staff': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'Tickets Assigned': [45, 38, 52, 41, 47],
    'Resolved': [42, 35, 46, 40, 44],
    'Resolution Rate %': [93.3, 92.1, 88.5, 97.6, 93.6]
})

it_col1, it_col2 = st.columns(2)

with it_col1:
    st.subheader("Staff Performance")
    st.dataframe(performance_data, use_container_width=True)

with it_col2:
    st.subheader("Performance Distribution")
    st.bar_chart(performance_data.set_index('Staff')['Resolution Rate %'])
