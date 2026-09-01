from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# --- Auth Schemas ---

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    email: str
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdateRequest(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    status: Optional[str] = None


class LoginResponse(BaseModel):
    id: int
    username: str
    email: str


# --- Chat Schemas ---

class CreateChatRequest(BaseModel):
    name: str = Field(..., min_length=1)
    member_ids: list[int] = []


class CreateDirectChatRequest(BaseModel):
    participant_id: int = Field(..., gt=0)


class AddMemberRequest(BaseModel):
    user_id: int = Field(..., gt=0)


class ChatMemberResponse(BaseModel):
    id: int
    username: str
    email: str
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class ChatResponse(BaseModel):
    id: int
    name: str
    type: str
    created_by: int
    created_at: Optional[datetime] = None


# --- Message Schemas ---

class SendMessageRequest(BaseModel):
    chat_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    content: str
    file_url: Optional[str] = None
    created_at: Optional[datetime] = None
    username: Optional[str] = None


# --- WebSocket Schemas ---

class WSMessage(BaseModel):
    type: str
    chat_id: int
    content: str
