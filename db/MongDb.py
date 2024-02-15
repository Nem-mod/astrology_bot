from pprint import pprint

import motor
from motor.motor_asyncio import AsyncIOMotorClient

from data.config import config

uri = ""


class MongoDbService:
    def __init__(self):
        self._client = AsyncIOMotorClient(config.database.mongo_url)
        self._db = self._client["astro_bot"]
        self._user_collection = self._db["users"]
        self._chat_collection = self._db["virtual_assistant_chat"]

    async def insert_user(self, document: dict):
        user = await self._user_collection.insert_one(document)
        return user

    async def get_user(self, user_id: int):
        user = await self._user_collection.find_one({"user_id": user_id})
        return user

    async def update_user(self, user_id: int, data: dict):
        user = await self._user_collection.update_one(
            filter={"user_id": user_id},
            update=data
        )
        return user

    async def delete_user(self, user_id: int):
        user = await self._user_collection.delete_one(
            filter={"user_id": user_id},
        )
        return user

    async def add_chat_message(self, chat_id: int, role: str, message: str):
        await self._chat_collection.insert_one(
            {
                "chat_id": chat_id,
                "role": role,
                "content": message
            }
        )
        return True

    async def get_chat_messages(self, chat_id: int, limit: int):
        cursor = self._chat_collection.find({"chat_id": chat_id}).sort({"$natural": -1}).limit(limit)
        messages = []
        for document in await cursor.to_list(length=100):
            messages.insert(0, document)
        return messages
