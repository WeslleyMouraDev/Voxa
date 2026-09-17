from enum import Enum


class TranscriptionMode(str, Enum):
    NORMAL = "normal"
    DYNAMIC = "dynamic"
    ACCELERATED = "accelerated"


class TaskStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
