from enum import Enum

class Platform(str, Enum):
    TWITTER = "Twitter"
    LINKEDIN = "LinkedIn"
    INSTAGRAM = "Instagram"
    FACEBOOK = "Facebook"

class PostStatus(str, Enum):
    DRAFT = "Draft"
    SCHEDULED = "Scheduled"
    POSTED = "Posted"

class Tone(str, Enum):
    PROFESSIONAL = "Professional"
    GEN_Z = "Gen-Z"
    FUNNY = "Funny"
    HYPE = "Hype"
