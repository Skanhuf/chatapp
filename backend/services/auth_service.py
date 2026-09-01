import bcrypt

from models.models import User
from repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, username: str, email: str, password: str) -> User:
        if len(username) < 3 or len(password) < 6:
            raise ValueError("username must be at least 3 characters, password at least 6")

        existing = await self.user_repo.find_by_username(username)
        if existing is not None:
            raise ValueError("username already taken")

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user = User(
            id=0,
            username=username,
            email=email,
            password_hash=password_hash,
            status="pending",
            created_at=None
        )

        return await self.user_repo.create(user)

    async def login(self, username: str, password: str) -> User:
        user = await self.user_repo.find_by_username(username)
        if user is None:
            raise ValueError("invalid credentials")

        if user.status != "approved":
            raise ValueError("account not approved")

        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise ValueError("invalid credentials")

        return user

    async def get_profile(self, user_id: int) -> User:
        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ValueError("user not found")
        return user

    async def update_profile(self, user_id: int, email: str) -> None:
        await self.user_repo.update_profile(user_id, email)

    async def search_users(self, query: str) -> list[User]:
        return await self.user_repo.search(query)
