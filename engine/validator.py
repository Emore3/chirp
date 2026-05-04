import re
from datetime import datetime
from typing import List, Tuple
from models.post import SocialPost
from storage.local import get_all_posts

class ScheduleConflictError(Exception):
    pass

def validate_post_content(content: str, platform: str) -> List[str]:
    """
    Validates content based on platform rules using regex.
    Returns a list of warning messages.
    """
    warnings = []
    
    # Check Hashtags
    hashtags = re.findall(r"(#[A-Za-z0-9_]+)", content)
    
    if platform == "Twitter" and len(hashtags) > 2:
        warnings.append(f"Twitter recommends 1-2 hashtags, you have {len(hashtags)}.")
    elif platform == "Instagram" and len(hashtags) < 3:
        warnings.append(f"Instagram posts perform better with more hashtags, you have {len(hashtags)}.")
        
    # Check Links
    links = re.findall(r"(https?://[^\s]+)", content)
    if platform == "Instagram" and links:
        warnings.append("Links are not clickable in Instagram captions.")
        
    # Character Limits
    if platform == "Twitter" and len(content) > 280:
        warnings.append(f"Twitter has a 280 character limit, this post is {len(content)} characters.")
        
    return warnings

def check_schedule_conflict(target_time: datetime, platform: str, post_id: str = None) -> bool:
    """
    Checks if there is a scheduling conflict for the given platform.
    Raises ScheduleConflictError if a conflict is found.
    """
    posts = get_all_posts()
    
    for post in posts:
        if post.id == post_id:
            continue
            
        if post.platform.value == platform and post.scheduled_time:
            # Check if times are exactly the same (or within a 5 min window)
            time_diff = abs((target_time - post.scheduled_time).total_seconds())
            if time_diff < 300: # 5 minutes
                raise ScheduleConflictError(
                    f"Conflict: Another post is already scheduled for {platform} at {post.scheduled_time.strftime('%Y-%m-%d %H:%M')}"
                )
    
    return False
