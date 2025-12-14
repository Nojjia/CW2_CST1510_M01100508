import streamlit as st
from app.data.db import connect_database
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.utility.user_validations import (validate_username, validate_password)

st.set_page_config(page_title="Multi-Domain Intelligence Platform", page_icon="🔐", layout="centered", initial_sidebar_state="collapsed")
conn = connect_database()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

st.header("Multi-Domain Intelligence Platform")
st.header("Project Overview")

st.markdown(f"""
**Course**: CST1510 - Programming 2  
**Week**: 9 - Web Interface, MVC & Visualization  
**Tier**: Multi-Domain Implementation (Cybersecurity, Data Science, IT Operations)
""")

st.subheader("Domain-Specific Problems Addressed")

st.subheader("Week 9 Implementation Status")
features_col1, features_col2, features_col3 = st.columns(3)

st.markdown("""
    ### Authentication
    Secure login with bcrypt hashing.
    Done
""")

st.markdown("""
    ### Database
    SQLite with 4 normalized tables
    Done
""")

st.markdown("""
    Visualizations
    Semi-done, not everything is icorporatef well
    Semi-Done
""")


# In Home.py, update the quick access section:
if st.session_state.logged_in:
    st.subheader("Quick Access")
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    with quick_col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    with quick_col2:
        if st.button("📈 Analytics", use_container_width=True):
            st.switch_page("pages/2_Analytics.py")
    with quick_col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/3_Settings.py")
    with quick_col4:
        if st.button("🤖 AI Assistant", use_container_width=True):
            st.switch_page("pages/5_AI_Chat.py")
    st.write(f"**Username**: {st.session_state.username}")
    st.write(f"**Role**: {st.session_state.role}")
    st.write(f"**Database**: Connected to `{conn}`")
    st.write(f"**Session ID**: `{id(st.session_state)}`")
    st.divider()
    if st.button("🚪 Logout", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()
    st.stop()

st.header("User Authentication")
tab_login, tab_register = st.tabs(["Login", "Register"])

with tab_login:
    st.subheader("Login to Your Account")
    st.write("MUST CLICK BOTH BUTTONS BEFORE PRESSING LOG IN")
    st.write("EVEN IF AUTOFILL USED.  OTHERWISE WILL NOT LOG IN")
    login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
    login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
    login_button = st.button("Log In", type="primary", use_container_width=True)
    if login_button:
        if not login_username or not login_password:
            st.error("Please enter both username and password.")
            st.stop()
        success, msg = login_user(conn, login_username, login_password)
        if success:
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.session_state.role = f"{msg}"
            st.success(f"✅ Login successful! Welcome, {login_username}.")
            
            with st.spinner("Redirecting to dashboard..."):
                import time
                time.sleep(1)
                st.switch_page("pages/1_Dashboard.py")
        else:
            st.error(f"{msg}")

with tab_register:
    st.subheader("Create New Account")
    
    new_username = st.text_input("Choose a username", key="reg_username", 
                                placeholder="4-20 characters, no spaces")
    new_password = st.text_input("Choose a password", type="password", 
                                key="register_password", placeholder="Minimum 6 characters")
    confirm_password = st.text_input("Confirm password", type="password", 
                                    key="register_confirm", placeholder="Re-enter your password")
    role = st.selectbox("Select role", ["user", "analyst", "admin"], 
                       help="Admins have full access, analysts have domain access, users have basic access")
    if new_password:
        from app.utility.user_validations import validate_password
        valid, pwd_msg = validate_password(new_password)
        if valid:
            if "STRONG" in pwd_msg:
                st.success(f"{pwd_msg}")
            elif "MEDIUM" in pwd_msg:
                st.warning(f"{pwd_msg}")
            else:
                st.error(f"{pwd_msg}")
    register_button = st.button("Create Account", type="primary", use_container_width=True)
    if register_button:
        if not new_username or not new_password or not confirm_password:
            st.warning("Please fill in all fields.")
            st.stop()
        if new_password != confirm_password:
            st.error("Passwords do not match.")
            st.stop()
        valid_user, user_msg = validate_username(new_username)
        if not valid_user:
            st.error(f"{user_msg}")
            st.stop()
        valid_pwd, pwd_msg = validate_password(new_password)
        if not valid_pwd:
            st.error(f"{pwd_msg}")
            st.stop()
        success, msg = register_user(conn, new_username, new_password, role)
        if success:
            st.success(f"{msg}")
            st.balloons()
            st.info(f"Password strength: {pwd_msg}")
            st.info("You can now log in from the Login tab.")
            st.rerun()
        else:
            st.error(f"{msg}")
