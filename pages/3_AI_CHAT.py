import streamlit as st
from google import genai
import time

st.set_page_config(
    page_title="AI Assistant | Intelligence Platform",
    page_icon="🤖",
    layout="wide"
)
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view this page")
    if st.button("Go to Login", key="go_login_ai"):
        st.switch_page("Home.py")
    st.stop()
# Initialize Gemini client
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    selected_model = "models/gemini-2.0-flash-exp"
    
except Exception as e:
    st.error(f"Failed to initialize Gemini: {e}")
    st.stop()
# --- Sidebar ---
with st.sidebar:
    st.subheader("User Panel")
    st.write(f"**Username:** {st.session_state.username}")
    st.write(f"**Role:** {st.session_state.role}")
    st.write(f"**Page:** AI Assistant")
    
    st.divider()
    
    st.subheader("📋 Navigation")
    nav_cols = st.columns(2)
    with nav_cols[0]:
        if st.button("📊 Dashboard", key="nav_dashboard_ai"):
            st.switch_page("pages/1_Dashboard.py")
        if st.button("📈 Analytics", key="nav_analytics_ai"):
            st.switch_page("pages/2_Analytics.py")
    with nav_cols[1]:
        if st.button("⚙️ Settings", key="nav_settings_ai"):
            st.switch_page("pages/3_Settings.py")
        if st.button("🗄️ Database", key="nav_database_ai"):
            st.switch_page("pages/4_Database_Viewer.py")
    
    st.divider()
    
    # Domain Selection
    st.subheader("🔄 Domain Expert")
    domain = st.selectbox(
        "Select Assistant Type",
        ["Cybersecurity", "Data Science", "IT Operations", "General"],
        key="ai_domain_selector"
    )
    
    # Model Settings
    st.subheader("⚙️ Settings")
    temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.7, 0.1,
        help="Higher = more creative, Lower = more focused",
        key="temp_slider_ai"
    )
    
    max_tokens = st.slider(
        "Max Length", 100, 4000, 1000, 100,
        help="Maximum response length",
        key="tokens_slider_ai"
    )
    
    if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat_ai"):
        st.session_state.conversation = []
        st.rerun()
    
    st.divider()
    
    if st.button("🚪 Logout", type="secondary", key="logout_ai"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.switch_page("Home.py")

# --- Main Content ---
st.title("🤖 Gemini AI Assistant")
st.caption(f"Domain: {domain} | Model: Gemini Flash")

# Initialize conversation
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Domain prompts
system_prompts = {
    "Cybersecurity": "You are a cybersecurity expert. Analyze threats, provide technical guidance, and recommend security measures.",
    "Data Science": "You are a data science expert. Help with analysis, visualization, and statistical methods.",
    "IT Operations": "You are an IT operations expert. Troubleshoot issues and optimize systems.",
    "General": "You are a helpful AI assistant."
}

# Display conversation history
for i, message in enumerate(st.session_state.conversation):
    role = message.get("role", "")
    content = message.get("content", "")
    if role and content:
        with st.chat_message(role):
            st.markdown(content)  # NO KEY HERE

# Chat input
prompt = st.chat_input(f"Ask the {domain} assistant...", key="chat_input_ai")

if prompt:
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)  # NO KEY HERE
    
    # Add to conversation
    st.session_state.conversation.append({"role": "user", "content": prompt})
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Build conversation context
            conversation_context = system_prompts[domain] + "\n\n"
            
            # Include last 5 messages for context
            recent_messages = st.session_state.conversation[-5:] if len(st.session_state.conversation) > 5 else st.session_state.conversation
            
            for msg in recent_messages:
                if msg["role"] == "user":
                    conversation_context += f"User: {msg['content']}\n"
                else:
                    conversation_context += f"Assistant: {msg['content']}\n"
            
            # Add current prompt
            conversation_context += f"User: {prompt}\nAssistant: "
            
            # Generate response
            response = client.models.generate_content(
                model=selected_model,
                contents=conversation_context,
            )
            
            # Extract response
            if hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)
            
            # Simulate streaming
            words = response_text.split()
            display_text = ""
            for i in range(min(30, len(words))):
                display_text = " ".join(words[:i+1])
                message_placeholder.markdown(display_text + "▌")  # NO KEY HERE
                time.sleep(0.03)
            
            # Show full response
            message_placeholder.markdown(response_text)  # NO KEY HERE
            
            # Store response
            st.session_state.conversation.append({
                "role": "assistant", 
                "content": response_text
            })
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"Error: {error_msg}")
            
            # Fallback
            fallback = f"I'm your {domain} assistant. Try rephrasing your question."
            message_placeholder.markdown(fallback)  # NO KEY HERE
            
            st.session_state.conversation.append({
                "role": "assistant", 
                "content": fallback
            })
