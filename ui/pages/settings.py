import streamlit as st
import os

st.title("⚙️ Settings")

st.markdown("### 🔑 API Configuration")
st.info("Your API key is stored locally in `.streamlit/secrets.toml` and is never sent to any server other than Google Gemini.")

# Function to save secret
def save_api_key(key: str):
    os.makedirs(".streamlit", exist_ok=True)
    with open(".streamlit/secrets.toml", "w") as f:
        f.write(f'GEMINI_API_KEY = "{key}"')
    st.success("API Key saved successfully! Please refresh or restart the app for it to take effect.")

# Current key status
current_key = None
try:
    current_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

if not current_key:
    current_key = os.environ.get("GEMINI_API_KEY")

if current_key:
    st.success("✅ Gemini API Key is configured.")
    if st.button("Change API Key"):
        st.session_state.show_key_input = True
else:
    st.warning("⚠️ Gemini API Key is not configured.")
    st.session_state.show_key_input = True

if st.session_state.get("show_key_input", False):
    new_key = st.text_input("Enter your Google Gemini API Key:", type="password")
    if st.button("Save Key"):
        if new_key:
            save_api_key(new_key)
            st.session_state.show_key_input = False
        else:
            st.error("Please enter a valid key.")

st.markdown("---")
st.markdown("### 🛠️ Data Management")
if st.button("🗑️ Clear Local CSV Cache"):
    if os.path.exists("data/posts.csv"):
        os.remove("data/posts.csv")
        st.success("Cleared all local post data.")
        st.rerun()
    else:
        st.info("No local data found to clear.")