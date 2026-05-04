import os
import pandas as pd
from datetime import datetime
from typing import List, Optional
from models.post import SocialPost
from models.enums import Platform, PostStatus, Tone

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "posts.csv")

def ensure_csv_exists():
    if not os.path.exists(os.path.dirname(CSV_FILE_PATH)):
        os.makedirs(os.path.dirname(CSV_FILE_PATH))
    if not os.path.exists(CSV_FILE_PATH):
        df = pd.DataFrame(columns=[
            "id", "content", "platform", "tone", "status", "scheduled_time", 
            "image_path", "likes", "shares", "comments", "created_at"
        ])
        df.to_csv(CSV_FILE_PATH, index=False)

def get_all_posts() -> List[SocialPost]:
    ensure_csv_exists()
    df = pd.read_csv(CSV_FILE_PATH)
    posts = []
    for _, row in df.iterrows():
        # Handle nan values from csv gracefully
        scheduled_str = str(row.get("scheduled_time", ""))
        scheduled_dt = datetime.fromisoformat(scheduled_str) if scheduled_str and scheduled_str != "nan" else None
        
        post = SocialPost(
            id=str(row["id"]),
            content=str(row["content"]),
            platform=Platform(row["platform"]),
            tone=Tone(row["tone"]),
            status=PostStatus(row["status"]),
            scheduled_time=scheduled_dt,
            image_path=str(row.get("image_path", "")) if str(row.get("image_path", "")) != "nan" else None,
            metrics={
                "likes": int(row.get("likes", 0)),
                "shares": int(row.get("shares", 0)),
                "comments": int(row.get("comments", 0))
            },
            created_at=datetime.fromisoformat(str(row["created_at"]))
        )
        posts.append(post)
    return posts

def save_post(post: SocialPost):
    ensure_csv_exists()
    df = pd.read_csv(CSV_FILE_PATH)
    post_dict = post.to_csv_dict()
    
    if post.id in df["id"].values:
        # Update existing
        index = df.index[df["id"] == post.id][0]
        for key, value in post_dict.items():
            df.at[index, key] = value
    else:
        # Append new
        new_row = pd.DataFrame([post_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        
    df.to_csv(CSV_FILE_PATH, index=False)

def delete_post(post_id: str):
    ensure_csv_exists()
    df = pd.read_csv(CSV_FILE_PATH)
    df = df[df["id"] != post_id]
    df.to_csv(CSV_FILE_PATH, index=False)
