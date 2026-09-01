from datetime import datetime

from pydantic import BaseModel, Field

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
    status: str | None = None


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
    status: str | None = None
    created_at: datetime | None = None


class ChatResponse(BaseModel):
    id: int
    name: str
    type: str
    created_by: int
    created_at: datetime | None = None


# --- Message Schemas ---

class SendMessageRequest(BaseModel):
    chat_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    content: str
    file_url: str | None = None
    created_at: datetime | None = None
    username: str | None = None


# --- WebSocket Schemas ---

class WSMessage(BaseModel):
    type: str
    chat_id: int
    content: str
