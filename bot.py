import logging
import pprint
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
from db import MongoDbService
from middlewares import StructLoggingMiddleware
from middlewares.scheduler import SchedulerMiddleware

routes = web.RouteTableDef()


@routes.post("/wallet/order")
async def apply_wallet_transaction(request: web.Request):
    bot = request.app["bot"]
    data = await request.json()
    print("---------------------------------$Transaction--------------------------")
    mongo_client = MongoDbService()
    pprint.pprint(data)
    for event in data:
        if event["type"] == "ORDER_PAID":
            data = event["payload"]
            custom_data: str = data["customData"]
            user_id, service_amount, service_type = custom_data.split("_")
            user_id = int(user_id)
            print("---------------------------------MONGO--------------------------")
            user = await mongo_client.get_user(user_id)
            if not user:
                continue
            if service_type == "nt":
                ctx_amount = "natal_chart_left"
            else:
                ctx_amount = ("assistant_questions_left")

            log = await mongo_client.update_user(user_id, {
                "$inc": {
                    ctx_amount: int(service_amount)
                }
            })
            print(log)

            locale = user["locale"]
            if locale == "ru":
                answer_msg = f"💰 Платеж прошел успешно."
            if locale == "uk":
                answer_msg = f"💰 Платіж пройшов успішно."
            else:
                answer_msg = f"💰 Payment was successful."
            await bot.send_message(chat_id=user_id, text=answer_msg)

    print("---------------------------------$--------------------------")
    return web.Response(status=200)


async def on_startup(bot: Bot):
    await bot.set_webhook(
        f"{WEB_SERVER_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET,
        max_connections=1000
    )
    print(WEB_SERVER_URL)
    pass


async def on_shut_down(bot: Bot):
    await bot.session.close()
    await bot.delete_webhook()


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


def main() -> None:
    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
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

    app = web.Application()
    app["bot"] = bot
    app.add_routes(routes)
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        handle_in_background=True
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    # TODO: create WEBSERVER_HOST_PAR
    web.run_app(app, host="0.0.0.0", port=WEB_SERVER_PORT)
    # await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
