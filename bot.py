import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import utils
from data.config import WEBHOOK_PATH, WEB_SERVER_URL, BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT
import controllers
from middlewares import StructLoggingMiddleware


async def on_startup(bot: Bot):
    await bot.set_webhook(
        f"{WEB_SERVER_URL}{WEBHOOK_PATH}",
        secret_token=None,
        max_connections=1000
    )


def init_routers(dp: Dispatcher):
    dp.include_router(controllers.user_router.prepare_router())


def setup_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))


def setup_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(type="aiogram")
    dp["db_logger"] = utils.logging.setup_logger().bind(type="db")
    dp["cache_logger"] = utils.logging.setup_logger().bind(type="cache")
    dp["business_logger"] = utils.logging.setup_logger().bind(type="business")


def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    init_routers(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")

def main() -> None:
    print(BOT_TOKEN)
    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    setup_aiogram(dp)

    dp.startup.register(on_startup)

    app = web.Application()
    # app.add_routes(routes)
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        handle_in_background=True
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
