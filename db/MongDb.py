from pprint import pprint

import motor
from motor.motor_asyncio import AsyncIOMotorClient

uri = ""


class MongoDbService:
    def __init__(self):
        self._client = AsyncIOMotorClient()
        self._db = self._client["astro_bot"]
        self._user_collection = self._db["users"]

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


mongo = MongoDbService()
