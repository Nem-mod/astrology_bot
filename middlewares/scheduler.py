from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator


class SchedulerMiddleware(BaseMiddleware):

    def __init__(self, scheduler: ContextSchedulerDecorator):
        self._scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
            *args: Any
    ) -> Any:
        data["apscheduler"] = self._scheduler
        return await handler(event, data)
