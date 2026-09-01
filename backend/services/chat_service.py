from repositories.chat_repo import ChatRepository
from repositories.user_repo import UserRepository
from models.models import Chat, User


class ChatService:
    def __init__(self, chat_repo: ChatRepository, user_repo: UserRepository):
        self.chat_repo = chat_repo
        self.user_repo = user_repo

    async def get_chats(self, user_id: int) -> list[Chat]:
        return await self.chat_repo.get_by_user_id(user_id)

    async def create_chat(self, name: str, created_by: int, member_ids: list[int] = None) -> Chat:
        if member_ids is None:
            member_ids = []

        chat = Chat(
            id=0, name=name, chat_type="group",
            created_by=created_by, created_at=None
        )

        chat = await self.chat_repo.create(chat)

        # Add creator as admin
        await self.chat_repo.add_member(chat.id, created_by, "admin")

        # Add other members
        for uid in member_ids:
            await self.chat_repo.add_member(chat.id, uid, "member")

        return chat

    async def create_direct_chat(self, user1_id: int, user2_id: int) -> int:
        return await self.chat_repo.create_direct_chat(user1_id, user2_id)

    async def get_members(self, chat_id: int) -> list[User]:
        return await self.chat_repo.get_members(chat_id)

    async def add_member(self, chat_id: int, user_id: int) -> None:
        await self.chat_repo.add_member(chat_id, user_id, "member")

    async def remove_member(self, chat_id: int, user_id: int) -> None:
        await self.chat_repo.remove_member(chat_id, user_id)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repo.find_by_id(user_id)
