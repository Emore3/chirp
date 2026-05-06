import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
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
    
    calendar_events = []
    for post in posts:
        if post.status == PostStatus.SCHEDULED and post.scheduled_time:
            # Pick a color based on platform
            color = "#1877F2" # default
            if post.platform.value == "Instagram": color = "#E1306C"
            elif post.platform.value == "Twitter": color = "#1DA1F2"
            elif post.platform.value == "LinkedIn": color = "#0077b5"
            
            calendar_events.append({
                "title": f"{post.platform.value}",
                "start": post.scheduled_time.isoformat(),
                "backgroundColor": color,
                "borderColor": color,
                "extendedProps": {
                    "content": post.content,
                    "id": post.id,
                    "tone": post.tone.value
                }
            })
            
    calendar_options = {
        "editable": False,
        "selectable": True,
        "height": 550,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "initialView": "dayGridMonth",
    }
    
    custom_css = """
        .fc-event-past { opacity: 0.8; }
        .fc-event-time { font-style: italic; }
        .fc-event-title { font-weight: 700; }
        .fc-toolbar-title { font-size: 1.5rem; }
    """

    cal = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css, key="content_calendar")
    
    if cal.get("eventClick"):
        event = cal["eventClick"]["event"]
        st.markdown("---")
        st.write("### 🔍 Selected Post Details")
        st.info(f"**Content:** {event['extendedProps']['content']}")
        
        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("🚀 Simulate Publish", key=f"pub_{event['extendedProps']['id']}"):
                target_post = next((p for p in posts if p.id == event['extendedProps']['id']), None)
                if target_post:
                    target_post.status = PostStatus.POSTED
                    target_post.metrics = simulate_engagement(target_post.platform.value, target_post.tone.value)
                    save_post(target_post)
                    st.success("Post marked as Live!")
                    st.rerun()

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
    st.subheader("📈 Performance Analytics")
    live_posts = [p for p in posts if p.status == PostStatus.POSTED]
    
    if not live_posts:
        st.info("No live posts yet. Simulate publishing a scheduled post to see metrics.")
    else:
        # --- High-Level Overview ---
        st.markdown("### Executive Summary")
        total_likes = sum(p.metrics.get("likes", 0) for p in live_posts)
        total_shares = sum(p.metrics.get("shares", 0) for p in live_posts)
        total_comments = sum(p.metrics.get("comments", 0) for p in live_posts)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Posts", len(live_posts))
        m2.metric("Total Likes", total_likes, delta=f"+{int(total_likes*0.1)} this week")
        m3.metric("Total Shares", total_shares, delta=f"+{int(total_shares*0.05)} this week")
        m4.metric("Total Comments", total_comments)
        
        st.markdown("---")
        
        # --- Platform Distribution (Plotly) ---
        st.markdown("### Engagement by Platform")
        data = []
        for p in live_posts:
            data.append({
                "Platform": p.platform.value,
                "Likes": p.metrics.get("likes", 0),
                "Shares": p.metrics.get("shares", 0),
                "Comments": p.metrics.get("comments", 0),
                "Content Snippet": p.content[:50] + "..."
            })
            
        df = pd.DataFrame(data)
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            likes_dist = df.groupby("Platform")["Likes"].sum().reset_index()
            fig = px.pie(likes_dist, values='Likes', names='Platform', title='Likes Distribution', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_chart2:
            eng_dist = df.groupby("Platform")[["Likes", "Shares", "Comments"]].sum().reset_index()
            fig2 = px.bar(eng_dist, x='Platform', y=['Likes', 'Shares', 'Comments'], title='Total Engagement Breakdown', barmode='group', color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig2, use_container_width=True)
            
        st.markdown("---")
        
        # --- Individual Post Metrics ---
        st.markdown("### Individual Post Performance")
        
        live_posts_sorted = sorted(live_posts, key=lambda p: p.created_at, reverse=True)
        
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search_query = st.text_input("🔍 Search posts by keyword")
        with col_f2:
            platforms_filter = st.multiselect("Filter by Platform", options=list(set(p.platform.value for p in live_posts_sorted)))
            
        filtered_posts = live_posts_sorted
        if search_query:
            filtered_posts = [p for p in filtered_posts if search_query.lower() in p.content.lower()]
        if platforms_filter:
            filtered_posts = [p for p in filtered_posts if p.platform.value in platforms_filter]
            
        if not filtered_posts:
            st.info("No posts match your filters.")
            
        for i, p in enumerate(filtered_posts):
            with st.expander(f"📱 {p.platform.value} | {p.tone.value} Tone | 👍 {p.metrics.get('likes', 0)} Likes"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown("**Content:**")
                    st.info(p.content)
                with c2:
                    st.markdown("**Metrics:**")
                    st.metric("Likes", p.metrics.get("likes", 0))
                    st.metric("Shares", p.metrics.get("shares", 0))
                    st.metric("Comments", p.metrics.get("comments", 0))

with tab4:
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
