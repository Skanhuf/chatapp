from models.models import Message
from repositories.chat_repo import ChatRepository
from repositories.message_repo import MessageRepository


class MessageService:
    def __init__(self, message_repo: MessageRepository, chat_repo: ChatRepository):
        self.message_repo = message_repo
        self.chat_repo = chat_repo

    async def send_message(self, message: Message) -> Message:
        return await self.message_repo.save(message)

    async def get_messages(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        return await self.message_repo.get_by_chat_id(chat_id, limit, offset)

    async def search_messages(self, chat_id: int, query: str) -> list[Message]:
        return await self.message_repo.search(chat_id, query)
