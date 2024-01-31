from loader import load_config

config = load_config()

WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_URL = config.server.url
WEB_SERVER_PORT = config.server.port
WEBHOOK_PATH = f"/bot/{config.bot.token}"

LOGGING_LEVEL = 10

BOT_TOKEN = config.bot.token
