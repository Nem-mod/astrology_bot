import asyncio
import datetime
import logging
import sys
import controllers
import utils

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.utils.i18n import FSMI18nMiddleware, I18n
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from aiohttp import web
from redis.asyncio import Redis
from data.config import WEBHOOK_PATH, WEB_SERVER_URL, BOT_TOKEN, WEB_SERVER_PORT, WEBHOOK_SECRET, \
    REDIS_SERVER
from middlewares import StructLoggingMiddleware
from middlewares.scheduler import SchedulerMiddleware


async def on_startup(bot: Bot):
    # await bot.set_webhook(
    #     f"{WEB_SERVER_URL}{WEBHOOK_PATH}",
    #     secret_token=WEBHOOK_SECRET,
    #     max_connections=1000
    # )
    # print(WEB_SERVER_URL)
    pass


async def on_shut_down(bot: Bot):
    await bot.session.close()
    # await bot.delete_webhook()


def init_routers(dp: Dispatcher):
    dp.include_router(controllers.user_router.prepare_router())
    dp.include_router(controllers.va_router.prepare_router())


def setup_middlewares(dp: Dispatcher, scheduler):
    i18n = I18n(path="locales", default_locale="en", domain="messages")
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))


def setup_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(type="aiogram")
    dp["db_logger"] = utils.logging.setup_logger().bind(type="db")
    dp["cache_logger"] = utils.logging.setup_logger().bind(type="cache")
    dp["business_logger"] = utils.logging.setup_logger().bind(type="business")


def setup_aiogram(dp: Dispatcher, scheduler) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    init_routers(dp)
    setup_middlewares(dp, scheduler)


async def current_time():
    print(f"\n\nAAAAAA --- {datetime.datetime.now()}\n\n")


async def clb_test(bot: Bot):
    await bot.send_message(
        chat_id=1483647254,
        text=f"\n\nAAAAAA --- {datetime.datetime.now()}\n\n"
    )


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    await bot.delete_webhook()
    if REDIS_SERVER.redis_enabled:
        storage = RedisStorage(
            redis=Redis(
                host=REDIS_SERVER.host,
                password=REDIS_SERVER.password,
                port=REDIS_SERVER.port,
                db=0,
            ),
            key_builder=DefaultKeyBuilder(with_bot_id=True)
        )

        job_stores = {
            'default': RedisJobStore(
                jobs_key='dispatched_trips_jobs',
                run_times_key='dispatched_trips_running',
                host=REDIS_SERVER.host,
                password=REDIS_SERVER.password,
                port=REDIS_SERVER.port,
                db=0,
            )
        }

        scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Europe/Kyiv", jobstores=job_stores))

    else:
        scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Europe/Kyiv"))
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    scheduler.ctx.add_instance(bot, declared_class=Bot)

    scheduler.start()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shut_down)
    setup_aiogram(dp, scheduler)

    # app = web.Application()
    #
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     handle_in_background=True
    # )
    #
    # webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    # setup_application(app, dp, bot=bot)
    # # TODO: create WEBSERVER_HOST_PAR
    # web.run_app(app, host="127.0.0.1", port=WEB_SERVER_PORT)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
