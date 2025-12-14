import streamlit as st
import bcrypt
from app.data.db import connect_database

st.set_page_config(
    page_title="Settings | Intelligence Platform", 
    page_icon="⚙️",
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
username = st.session_state.username
role = st.session_state.role

# Sidebar (Matching Dashboard)
with st.sidebar:
    st.subheader("🔐 User Panel")
    
    st.write(f"**Username:** {username}")
    st.write(f"**Role:** {role}")
    st.write(f"**Page:** Settings")
    
    st.divider()
    
    st.subheader("📋 Navigation")
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")
    
    if st.button("📈 Analytics", use_container_width=True):
        st.switch_page("pages/2_Analytics.py")
    
    if st.button("⚙️ Settings", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Settings.py")
    
    if st.button("🗄️ Database", use_container_width=True):
        st.switch_page("pages/4_Database_Viewer.py")
    
    st.divider()
    
    # Settings Quick Links
    st.subheader("⚙️ Quick Settings")
    
    if st.button("🔐 Change Password", use_container_width=True):
        st.session_state.settings_section = "password"
        st.rerun()
    
    if st.button("👤 Profile Info", use_container_width=True):
        st.session_state.settings_section = "profile"
        st.rerun()
    
    if st.button("🕒 Session", use_container_width=True):
        st.session_state.settings_section = "session"
        st.rerun()
    
    st.divider()
    
    # Logout Button
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.switch_page("Home.py")

# Main Content
st.title('⚙️ User Settings & Configuration')
st.text('Manage your account and preferences')

st.success(f"Welcome to settings, **{username}**!")

# User Profile Card
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("👤 User Profile")
    
    # Get user info from database
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, created_at FROM users WHERE username = ?", (username,))
    user_info = cursor.fetchone()
    
    if user_info:
        st.markdown(f"""
        **Username:** `{user_info[0]}`
        
        **Role:** `{user_info[1]}`
        
        **Account Created:** `{user_info[2]}`
        
        **Account ID:** `user_{hash(username) % 10000:04d}`
        """)
    else:
        st.warning("User information not found")

with col2:
    st.subheader("🛡️ Account Status")
    st.success("✅ Active")
    st.info("🔐 Password: Set")
    st.warning("⚠️ Last login: Today")

st.divider()

# Change Password Section
st.subheader("🔐 Change Password")

with st.form("change_password_form"):
    st.write("Update your account password")
    
    
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    password_strength = st.progress(0)
    
    # Update password strength
    if new_password:
        strength = min(len(new_password) * 10, 100)
        password_strength.progress(strength)
    
    submit_col1, submit_col2 = st.columns([3, 1])
    
    submitted = st.form_submit_button("Update Password", type="primary")
    
    if submitted:
        # Verify current password
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            st.error("User not found in database")
        elif not bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
            st.error("❌ Current password is incorrect")
        elif new_password != confirm_password:
            st.error("❌ New passwords do not match")
        elif len(new_password) < 6:
            st.error("❌ Password must be at least 6 characters")
        else:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (hashed.decode('utf-8'), username)
            )
            conn.commit()
            st.success("✅ Password updated successfully!")

st.divider()
st.subheader("🕒 Session Management")

session_col1, session_col2, session_col3 = st.columns(3)

with session_col1:
    st.metric("Active Sessions", "1", "Current")
    if st.button("🔄 Refresh Session", use_container_width=True):
        st.success("Session refreshed!")
        st.rerun()

with session_col2:
    st.metric("Session Duration", "15m", "+5m")
    if st.button("📱 End Other Sessions", use_container_width=True):
        st.warning("All other sessions have been terminated")
        st.info("This is a mock implementation - in a real app, this would clear session tokens")

with session_col3:
    st.metric("Login History", "24", "+2 this week")
    if st.button("📊 View History", use_container_width=True):
        st.info("Login history would be displayed here")

# Preferences
st.divider()
st.subheader("⚙️ Preferences")

pref_col1, pref_col2 = st.columns(2)

with pref_col1:
    st.write("**Display Settings**")
    theme = st.selectbox("Theme", ["Light", "Dark", "System Default"])
    language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
    
    if st.button("Save Display Settings", use_container_width=True):
        st.success("Display settings saved!")

st.divider()
st.subheader("⚠️ Danger Zone")

with st.expander("Delete Account and Data", expanded=False):
    st.warning("This action is permanent and cannot be undone!")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        confirm_text = st.text_input(
            "Type 'DELETE MY ACCOUNT' to confirm",
            placeholder="DELETE MY ACCOUNT",
            help="This will permanently delete your account and all associated data"
        )
    
    with col2:
        delete_enabled = confirm_text == "DELETE MY ACCOUNT"
        if st.button("Permanently Delete", 
                    type="secondary", 
                    disabled=not delete_enabled,
                    use_container_width=True):
            st.error("Account deletion would be implemented here")
            st.info("This is a safety feature - account deletion is disabled in this demo")