import streamlit as st
import pandas as pd
from storage.local import get_all_posts, CSV_FILE_PATH, save_post
from storage.importer import import_csv_calendar
from engine.analytics import simulate_engagement
from models.enums import PostStatus
from datetime import datetime

st.title("📊 Dashboard & Content Calendar")

posts = get_all_posts()

# --- Top Level Metrics ---
total_posts = len(posts)
scheduled_posts = len([p for p in posts if p.status == PostStatus.SCHEDULED])
posted_posts = len([p for p in posts if p.status == PostStatus.POSTED])

col1, col2, col3 = st.columns(3)
col1.metric("Total Drafts/Posts", total_posts)
col2.metric("Scheduled", scheduled_posts)
col3.metric("Live (Posted)", posted_posts)

st.markdown("---")

# --- Tabs for different views ---
tab1, tab2, tab3, tab4 = st.tabs(["📅 Visual Calendar", "📝 Drafts", "📈 Analytics", "📁 CSV Bulk Tools"])

with tab1:
    st.subheader("Upcoming Content")
    
    # Very simple visual calendar approximation using columns and cards
    # Real applications might use streamlit-calendar or similar community components
    
    scheduled = [p for p in posts if p.status == PostStatus.SCHEDULED and p.scheduled_time]
    scheduled.sort(key=lambda x: x.scheduled_time)
    
    if not scheduled:
        st.info("No scheduled posts. Go to 'Create Post' to schedule some content!")
    else:
        for post in scheduled:
            with st.container():
                st.markdown(f"**{post.scheduled_time.strftime('%b %d, %Y - %I:%M %p')}** | 📱 {post.platform.value}")
                st.caption(f"_{post.tone.value} Tone_")
                st.write(post.content[:100] + "..." if len(post.content) > 100 else post.content)
                
                # Action to simulate "Posting"
                if st.button(f"Simulate Publish", key=f"pub_{post.id}"):
                    post.status = PostStatus.POSTED
                    post.metrics = simulate_engagement(post.platform.value, post.tone.value)
                    save_post(post)
                    st.success("Post marked as Live!")
                    st.rerun()
                st.divider()

with tab2:
    st.subheader("Manage Drafts")
    draft_posts = [p for p in posts if p.status == PostStatus.DRAFT]
    if not draft_posts:
        st.info("No drafts found.")
    else:
        for post in draft_posts:
            with st.expander(f"Draft: {post.platform.value} ({post.tone.value})"):
                new_content = st.text_area("Edit Draft", value=post.content, key=f"edit_{post.id}")
                col_x, col_y = st.columns(2)
                if col_x.button("🚀 Publish Now", key=f"pub_draft_{post.id}"):
                    post.content = new_content
                    post.status = PostStatus.POSTED
                    post.metrics = simulate_engagement(post.platform.value, post.tone.value)
                    save_post(post)
                    st.success("Published!")
                    st.rerun()
                if col_y.button("🗑️ Delete", key=f"del_draft_{post.id}"):
                    from storage.local import delete_post
                    delete_post(post.id)
                    st.success("Deleted.")
                    st.rerun()

with tab3:
    st.subheader("Simulated Engagement Metrics")
    live_posts = [p for p in posts if p.status == PostStatus.POSTED]
    
    if not live_posts:
        st.info("No live posts yet. Simulate publishing a scheduled post to see metrics.")
    else:
        # Aggregate metrics
        data = []
        for p in live_posts:
            data.append({
                "Platform": p.platform.value,
                "Likes": p.metrics.get("likes", 0),
                "Shares": p.metrics.get("shares", 0),
                "Comments": p.metrics.get("comments", 0)
            })
            
        df = pd.DataFrame(data)
        
        # Simple Bar Chart for Likes per Platform
        st.write("Likes Distribution")
        likes_dist = df.groupby("Platform")["Likes"].sum()
        st.bar_chart(likes_dist)
        
        st.write("Raw Data")
        st.dataframe(df)

with tab3:
    st.subheader("CSV Import / Export")
    
    st.write("Download your current calendar as a CSV:")
    with open(CSV_FILE_PATH, "r", encoding="utf-8") as f:
        csv_data = f.read()
    st.download_button("Download posts.csv", data=csv_data, file_name="content_calendar.csv", mime="text/csv")
    
    st.write("Upload a CSV Content Calendar to bulk schedule:")
    uploaded_csv = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_csv:
        if st.button("Import Data"):
            success, errors = import_csv_calendar(uploaded_csv.getvalue())
            if success > 0:
                st.success(f"Successfully imported {success} posts!")
            if errors:
                st.error("Errors encountered during import:")
                for e in errors:
                    st.write(f"- {e}")
            if success > 0:
                st.rerun()
