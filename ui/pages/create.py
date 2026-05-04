import streamlit as st
import os
from datetime import datetime
from models.enums import Platform, Tone, PostStatus
from models.post import SocialPost
from storage.local import save_post
from ai.generator import setup_gemini, generate_social_post
from ui.mockups import render_mobile_preview

st.set_page_config(page_title="Create Content - Chirp", page_icon="✍️", layout="wide")

st.title("✨ Content Creator")
st.markdown("Generate platform-optimized content and schedule your simulated posts.")

# --- API Key Logic ---
api_key = None
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ Gemini API Key not found. Please set it in the Settings page.")
    st.stop()

setup_gemini(api_key)

# --- Session State Initialization ---
if "drafts" not in st.session_state:
    st.session_state.drafts = {} # platform -> content

# --- Input Section ---
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_area(
            "What's the topic or core message?", 
            placeholder="E.g., We are launching our new sustainable packaging today! #eco #sustainability",
            height=120
        )
    
    with col2:
        tone = st.selectbox("Brand Voice / Tone", options=[t.value for t in Tone])
        platforms = st.multiselect(
            "Target Platforms",
            options=[p.value for p in Platform],
            default=[p.value for p in Platform]
        )
        uploaded_image = st.file_uploader("Multimodal Vision (Optional)", type=["png", "jpg", "jpeg"])

    if st.button("🚀 Generate Content Variations", use_container_width=True, type="primary"):
        if not topic and not uploaded_image:
            st.error("Please provide either a topic or an image.")
        elif not platforms:
            st.error("Please select at least one platform.")
        else:
            image_path = None
            if uploaded_image:
                os.makedirs("uploads", exist_ok=True)
                image_path = os.path.join("uploads", uploaded_image.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
            
            with st.spinner("Gemini is crafting your posts..."):
                for p in platforms:
                    content = generate_social_post(
                        topic=topic or "Write a caption for this image",
                        platform=p,
                        tone=tone,
                        image_path=image_path
                    )
                    st.session_state.drafts[p] = {
                        "content": content,
                        "image_path": image_path,
                        "tone": tone
                    }
                    # Manually update the widget's session state key to show the new content
                    st.session_state[f"edit_{p}"] = content
            st.success("Drafts generated!")

# --- Output Section ---
if st.session_state.drafts:
    st.markdown("---")
    st.subheader("📝 Review & Schedule")
    
    # Use tabs for a cleaner platform-by-platform UI
    tabs = st.tabs([f"📱 {p}" for p in st.session_state.drafts.keys()])
    
    for i, (platform_name, data) in enumerate(st.session_state.drafts.items()):
        with tabs[i]:
            col_preview, col_controls = st.columns([1, 1.2])
            
            with col_preview:
                st.markdown("**Live Mobile Mockup**")
                # Get the current content from session state if it exists, else use the generated content
                current_content = st.session_state.get(f"edit_{platform_name}", data["content"])
                render_mobile_preview(current_content, platform_name, data["image_path"])
            
            with col_controls:
                edited_content = st.text_area(
                    "Refine Content", 
                    value=data["content"], 
                    height=250, 
                    key=f"edit_{platform_name}"
                )
                
                st.markdown("#### Action Center")
                
                # Update state if content changed
                st.session_state.drafts[platform_name]["content"] = edited_content
                
                # Sub-container for scheduling
                with st.container(border=True):
                    st.markdown("**Schedule for Later**")
                    c1, c2 = st.columns(2)
                    d = c1.date_input("Select Date", key=f"date_{platform_name}")
                    t = c2.time_input("Select Time", key=f"time_{platform_name}")
                    
                    if st.button(f"⏰ Schedule {platform_name} Post", key=f"btn_sched_{platform_name}", use_container_width=True):
                        dt = datetime.combine(d, t)
                        post = SocialPost(
                            content=edited_content,
                            platform=Platform(platform_name),
                            tone=Tone(data["tone"]),
                            image_path=data["image_path"],
                            status=PostStatus.SCHEDULED,
                            scheduled_time=dt
                        )
                        save_post(post)
                        st.balloons()
                        st.success(f"Successfully scheduled for {dt.strftime('%b %d, %H:%M')}!")

                st.markdown("OR")
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button(f"🚀 Publish Now", key=f"btn_pub_{platform_name}", use_container_width=True):
                    from engine.analytics import simulate_engagement
                    post = SocialPost(
                        content=edited_content,
                        platform=Platform(platform_name),
                        tone=Tone(data["tone"]),
                        image_path=data["image_path"],
                        status=PostStatus.POSTED,
                        metrics=simulate_engagement(platform_name, data["tone"])
                    )
                    save_post(post)
                    st.success("Post is now LIVE!")
                
                if col_btn2.button(f"💾 Save as Draft", key=f"btn_draft_{platform_name}", use_container_width=True):
                    post = SocialPost(
                        content=edited_content,
                        platform=Platform(platform_name),
                        tone=Tone(data["tone"]),
                        image_path=data["image_path"],
                        status=PostStatus.DRAFT
                    )
                    save_post(post)
                    st.info("Draft saved to Dashboard.")
