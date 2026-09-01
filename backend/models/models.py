from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, approved, blocked
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="user")
    chats = relationship("ChatMember", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    chat_type = Column(String, nullable=False)  # group, direct
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("ChatMember", back_populates="chat")
    messages = relationship("Message", back_populates="chat")


class ChatMember(Base):
    __tablename__ = "chat_members"

    chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
    user_id = Column(Integer, nullable=False, primary_key=True)
    role = Column(String, nullable=False, default="member")  # admin, member

    chat = relationship("Chat", back_populates="members")
    user = relationship("User", back_populates="chats")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    file_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")
