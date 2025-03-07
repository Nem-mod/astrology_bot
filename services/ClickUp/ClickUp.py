import json
import pprint
from enum import Enum

from aiogram.client.session import aiohttp

from data.config import config

CLICK_UP_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": config.clickup.token
}
CLICKUP_CRM_ID = config.clickup.crm_id


class CRM_CUSTOM_FIELDS(str, Enum):
    TELEGRAM_ID = "cd228d63-d118-406b-903f-97b03209ddc0",
    SEX = "64d2a760-ed3c-4424-b33d-428979b559fe"
    BIRTHDAY = "c860a287-52b1-4095-9339-1dfe4bba877e",
    BIRTHTIME = "14eb889b-6164-4fff-9d1c-0389416a6c3f",
    ARTICLE_LINK = "e9560160-fe39-4140-9888-a8ce29040950",
    TOPICS = "81700ed7-6a79-43fc-af07-452d7247aef8",
    NATAL_NAME = "ac211483-8753-4f8b-a10e-1138e9107afe",
    REGISTRATION_DATE = "2b36f0db-1bc1-4a87-a585-09aa4f742ead",
    LANGUAGE = "678a1db5-3476-4722-9d23-3f5d5f8a6665",
    LOCATION = "9976256f-ce2c-4f3e-a9c5-c445062473e8",
    NATAL_COUNT = "e06c57f8-2c94-45fa-9306-68f15e01b459"

class ClickUpService:
    @staticmethod
    async def update_task_custom_field(task_id: str, field_id: CRM_CUSTOM_FIELDS, value, *args, **kwargs):
        try:
            async with aiohttp.ClientSession(headers=CLICK_UP_HEADERS) as session:
                url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id.value}"
                data = {
                    "value": value,
                    **kwargs
                }
                data = json.dumps(data)
                async with session.post(url=url, data=data) as resp:
                    response = await resp.json()
                    return response
        except Exception as err:
            print(err)

    @staticmethod
    async def update_task_custom_status(task_id: str, value: str):
        try:
            async with aiohttp.ClientSession(headers=CLICK_UP_HEADERS) as session:
                url = f"https://api.clickup.com/api/v2/task/{task_id}"
                data = {
                    "status": value
                }
                data = json.dumps(data)
                async with session.put(url=url, data=data) as resp:
                    response = await resp.json()
                    return response
        except Exception as err:
            print(err)

    @staticmethod
    async def update_task_name(task_id: str, value: str):
        try:
            async with aiohttp.ClientSession(headers=CLICK_UP_HEADERS) as session:
                url = f"https://api.clickup.com/api/v2/task/{task_id}"
                data = {
                    "name": value
                }
                data = json.dumps(data)
                async with session.put(url=url, data=data) as resp:
                    response = await resp.json()
                    return response
        except Exception as err:
            print(err)


    @staticmethod
    async def add_to_crm(telegram: str, client_name: str, client_company: str = None, client_needs: str = None,
                         business_sphere: str = None,
                         additional_info: str = None, client_work_amount: str = None,
                         client_integration_preferences: str = None,
                         budget_range: str = None):
        async with aiohttp.ClientSession(headers=CLICK_UP_HEADERS) as session:
            url = f"https://api.clickup.com/api/v2/list/{CLICKUP_CRM_ID}/task"
            data = {
                "name": client_name,
                "notify_all": True,
                "custom_fields": [
                    {
                        "id": CRM_CUSTOM_FIELDS.TELEGRAM_ID,
                        "value": f"https://t.me/{telegram}"
                    }
                ]
            }
            data = json.dumps(data)
            async with session.post(url=url, data=data) as resp:
                response = await resp.json()
                return response

    @staticmethod
    async def get_record(record_id: str):
        async with aiohttp.ClientSession(headers=CLICK_UP_HEADERS) as session:
            url = f"https://api.clickup.com/api/v2/task/{record_id}"
            async with session.get(url=url) as resp:
                response = await resp.json()
                return response
