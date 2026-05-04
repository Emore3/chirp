import random
from datetime import datetime, timedelta

def suggest_best_time(platform: str) -> datetime:
    """
    A simple heuristic engine to suggest the best posting time.
    Returns a suggested datetime in the future.
    """
    now = datetime.now()
    
    # Simple hardcoded rules for now
    best_hours = {
        "Twitter": [9, 12, 17], # 9 AM, 12 PM, 5 PM
        "LinkedIn": [8, 10, 12], # Morning professional hours
        "Instagram": [11, 13, 19], # Lunch break, evening
        "Facebook": [13, 15, 20] # Afternoon slump, late evening
    }
    
    hours = best_hours.get(platform, [12])
    
    # Find the next available "best hour" today or tomorrow
    target_hour = random.choice(hours)
    
    suggested_time = now.replace(hour=target_hour, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)
    
    if suggested_time <= now:
        # Move to tomorrow
        suggested_time += timedelta(days=1)
        
    return suggested_time
