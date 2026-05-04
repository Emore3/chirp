import streamlit as st
import os
from PIL import Image
from models.enums import Platform, Tone
from models.post import SocialPost
from storage.local import save_post
from ai.generator import setup_gemini, generate_social_post

st.title("✍️ Create Post")

# API Key Check
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("Enter Gemini API Key to continue:", type="password")
    if not api_key:
        st.warning("Please enter an API key or set GEMINI_API_KEY in your environment.")
        st.stop()

setup_gemini(api_key)

with st.form("create_post_form"):
    topic = st.text_area("What do you want to post about?", placeholder="E.g., Launching our new smart orchestrator tool...")
    
    col1, col2 = st.columns(2)
    with col1:
        # Multi-select for platforms, defaulting to all
        platforms = st.multiselect(
            "Select Platforms",
            options=[p.value for p in Platform],
            default=[p.value for p in Platform]
        )
    with col2:
        tone = st.selectbox("Select Tone", options=[t.value for t in Tone])
        
    st.markdown("### Optional Visuals")
    uploaded_image = st.file_uploader("Upload an image for Vision-to-Caption AI generation", type=["png", "jpg", "jpeg"])
    
    submitted = st.form_submit_button("✨ Generate & Save Drafts")

if submitted:
    if not topic and not uploaded_image:
        st.error("Please provide either a topic or an image.")
    elif not platforms:
        st.error("Please select at least one platform.")
    else:
        # Save image locally if uploaded
        image_path = None
        if uploaded_image:
            # Ensure uploads directory exists
            os.makedirs("uploads", exist_ok=True)
            image_path = os.path.join("uploads", uploaded_image.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            
            st.image(uploaded_image, caption="Uploaded Image", width=300)
            
        st.success(f"Generating content for {len(platforms)} platforms...")
        
        # Display results
        for platform_val in platforms:
            with st.expander(f"📱 {platform_val} Draft", expanded=True):
                with st.spinner(f"Generating for {platform_val}..."):
                    generated_text = generate_social_post(
                        topic=topic or "Write a caption for this image", 
                        platform=platform_val, 
                        tone=tone,
                        image_path=image_path
                    )
                    
                    st.text_area("Content", value=generated_text, height=150, key=f"text_{platform_val}")
                    
                    # Save to DB as Draft
                    post = SocialPost(
                        content=generated_text,
                        platform=Platform(platform_val),
                        tone=Tone(tone),
                        image_path=image_path
                    )
                    save_post(post)
                    st.success(f"Saved as draft for {platform_val}!")
