import streamlit as st
import cohere
import os
from datetime import datetime

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "Chatbot", "content": "How can I help you today?"}]

# --- Cohere API Setup ---
@st.cache_resource
def init_cohere_client():
    COHERE_API_KEY = st.secrets.get("COHERE_API_KEY", os.environ.get("COHERE_API_KEY"))
    if not COHERE_API_KEY:
        st.error("API key not configured")
        st.stop()
    try:
        return cohere.Client(COHERE_API_KEY)
    except Exception as e:
        st.error(f"Client init failed: {str(e)}")
        st.stop()

co = init_cohere_client()

# --- Usage Tracking ---
if "api_usage" not in st.session_state:
    st.session_state.api_usage = {"count": 0, "last_used": None}

def query_cohere(prompt):
    try:
        # Convert roles to Cohere's expected format
        role_mapping = {
            "assistant": "Chatbot",
            "user": "User",
            "system": "System"
        }
        
        chat_history = [
            {
                "role": role_mapping.get(msg["role"], "User"),  # Default to "User" if unknown
                "message": msg["content"]
            }
            for msg in st.session_state.messages[:-1]
        ]
        
        response = co.chat(
            message=prompt,
            chat_history=chat_history,
            model="command-r",
            temperature=0.7
        )
        
        st.session_state.api_usage["count"] += 1
        st.session_state.api_usage["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return response.text
        
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- Streamlit UI ---
st.title("🤖 Chat.ai")

# Display messages (using consistent role names)
for message in st.session_state.messages:
    with st.chat_message("user" if message["role"] == "User" else "assistant"):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Store as "User" role for Cohere
    st.session_state.messages.append({"role": "User", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_cohere(prompt)
            st.markdown(response)
    
    # Store response as "Chatbot" role
    st.session_state.messages.append({"role": "Chatbot", "content": response})