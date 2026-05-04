import random
from typing import Dict

def simulate_engagement(platform: str, tone: str) -> Dict[str, int]:
    """
    Simulates realistic engagement metrics based on the platform and tone.
    Used when a post transitions from SCHEDULED to POSTED.
    """
    # Base multipliers
    platform_multiplier = {
        "Twitter": 1.0,
        "LinkedIn": 0.8,
        "Instagram": 2.5,
        "Facebook": 1.2
    }
    
    tone_multiplier = {
        "Professional": 1.0,
        "Gen-Z": 1.5,
        "Funny": 1.3,
        "Hype": 1.8
    }
    
    base_likes = random.randint(10, 100)
    base_shares = random.randint(0, 20)
    base_comments = random.randint(2, 30)
    
    mult = platform_multiplier.get(platform, 1.0) * tone_multiplier.get(tone, 1.0)
    
    return {
        "likes": int(base_likes * mult),
        "shares": int(base_shares * mult),
        "comments": int(base_comments * mult)
    }
