# enums.py
from enum import Enum

class AppMode(str, Enum):
    story = "story"
    learn = "learn"
    explorer = "explorer"

class VoiceStyle(str, Enum):
    friendly_cartoon = "friendly_cartoon"
    story_narrator = "story_narrator"

class ObjectCategory(str, Enum):
    animals = "animals"
    vehicles = "vehicles"
    toys = "toys"
    household_objects = "household_objects"

class ResponseType(str, Enum):
    story = "story"
    learn = "learn"
    explorer = "explorer"
    fallback = "fallback"

class SessionStatus(str, Enum):
    connecting = "connecting"
    active = "active"
    listening = "listening"
    speaking = "speaking"
    interrupted = "interrupted"
    resuming = "resuming"
    ended = "ended"
    failed = "failed"
