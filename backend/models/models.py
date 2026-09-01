from datetime import datetime


class User:
    def __init__(self, id: int, username: str, email: str, password_hash: str,
                 status: str, created_at: datetime):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.status = status  # pending, approved, blocked
        self.created_at = created_at


class Chat:
    def __init__(self, id: int, name: str, chat_type: str, created_by: int,
                 created_at: datetime):
        self.id = id
        self.name = name
        self.type = chat_type  # group, direct
        self.created_by = created_by
        self.created_at = created_at


class ChatMember:
    def __init__(self, chat_id: int, user_id: int, role: str):
        self.chat_id = chat_id
        self.user_id = user_id
        self.role = role  # admin, member


class Message:
    def __init__(self, id: int, chat_id: int, user_id: int, content: str,
                 file_url: str | None, created_at: datetime, username: str | None):
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id
        self.content = content
        self.file_url = file_url
        self.created_at = created_at
        self.username = username
