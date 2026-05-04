import streamlit as st
import os

# Set global page config
st.set_page_config(
    page_title="Chirp - Social Media Orchestrator",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation setup (using Streamlit 1.36+ st.navigation)
def main():
    st.sidebar.title("🐦 Chirp")
    st.sidebar.markdown("Your smart social media orchestrator.")
    
    # Define pages
    create_page = st.Page("ui/pages/create.py", title="Create Post", icon="✍️")
    dashboard_page = st.Page("ui/pages/dashboard.py", title="Dashboard & Calendar", icon="📊")
    settings_page = st.Page("ui/pages/settings.py", title="Settings", icon="⚙️")
    
    # Initialize navigation
    pg = st.navigation([create_page, dashboard_page, settings_page])
    pg.run()

if __name__ == "__main__":
    # Ensure ui/pages directory exists for dummy files
    os.makedirs("ui/pages", exist_ok=True)
    # Create empty files so streamlit doesn't crash before we build them
    for page in ["create.py", "dashboard.py", "settings.py"]:
        path = f"ui/pages/{page}"
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(f"import streamlit as st\nst.title('{page.replace('.py', '').capitalize()}')")
                
    main()
