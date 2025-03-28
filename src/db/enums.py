from enum import Enum


class SessionMode(Enum):
    GPT = "gpt"
    TALK = "talk"
    QUIZ = "quiz"
    RANDOM = "random"


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
