from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field
from uuid import uuid4
from models.enums import Platform, PostStatus, Tone

class SocialPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    platform: Platform
    tone: Tone
    status: PostStatus = PostStatus.DRAFT
    scheduled_time: Optional[datetime] = None
    image_path: Optional[str] = None
    metrics: Dict[str, int] = Field(default_factory=lambda: {"likes": 0, "shares": 0, "comments": 0})
    created_at: datetime = Field(default_factory=datetime.now)

    def to_csv_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "platform": self.platform.value,
            "tone": self.tone.value,
            "status": self.status.value,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else "",
            "image_path": self.image_path or "",
            "likes": self.metrics.get("likes", 0),
            "shares": self.metrics.get("shares", 0),
            "comments": self.metrics.get("comments", 0),
            "created_at": self.created_at.isoformat()
        }
