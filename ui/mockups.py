import streamlit as st
import os
import base64
from pathlib import Path
import streamlit.components.v1 as components

# Define paths to assets
ASSETS_DIR = Path(__file__).parent / "assets"
CSS_PATH = ASSETS_DIR / "phone_mockup.css"
HTML_PATH = ASSETS_DIR / "phone_mockup.html"

def load_asset(path: Path) -> str:
    """Helper to load text assets from the assets directory."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error loading asset from {path}: {e}")
        return ""

def render_mobile_preview(content: str, platform: str, image_path: str = None):
    """
    Renders a CSS-styled mobile phone mockup containing the post preview.
    Loads styles and structure from separate asset files.
    """
    
    # 1. Load Assets
    css_content = load_asset(CSS_PATH)
    html_template = load_asset(HTML_PATH)
    
    # 2. Prepare Platform Data
    platform_map = {
        "Twitter": {"name": "Twitter User", "handle": "@chirp_user", "badge": "Twitter"},
        "LinkedIn": {"name": "LinkedIn Professional", "handle": "Professional Connection", "badge": "LinkedIn"},
        "Instagram": {"name": "Insta Creator", "handle": "chirp_gram", "badge": "Instagram"},
        "Facebook": {"name": "Facebook User", "handle": "Friends of Chirp", "badge": "Facebook"}
    }
    
    p_info = platform_map.get(platform, {"name": "User", "handle": "@user", "badge": "Social"})
    
    # 3. Handle Image Encoding
    img_tag = ""
    if image_path and os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode()
            img_tag = f'<div class="post-image-container"><img src="data:image/png;base64,{b64_string}" class="mobile-image"></div>'
        except Exception as e:
            img_tag = f'<div style="color:red">Error loading image: {e}</div>'
    
    # 4. Inject Data into HTML Template
    mockup_html = html_template.format(
        username=p_info['name'],
        handle=p_info['handle'],
        badge=p_info['badge'],
        content=content,
        img_tag=img_tag
    )
    
    # 5. Assemble and Render
    full_html = f"""
    <html>
        <head>
            <style>{css_content}</style>
        </head>
        <body>
            {mockup_html}
        </body>
    </html>
    """
    
    components.html(full_html, height=650)
