from dataclasses import dataclass

from environs import Env


@dataclass
class TelegramBot:
    token: str
    # admin: str


@dataclass
class HttpClient:
    url: str
    port: int
    webhook_secret: str


@dataclass
class OpenAI:
    token: str


@dataclass
class RedisStorage:
    host: str
    port: int
    password: str
    redis_enabled: bool


@dataclass
class Config:
    bot: TelegramBot
    server: HttpClient
    openai: OpenAI
    redis: RedisStorage


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        bot=TelegramBot(
            token=env.str("BOT_TOKEN"),
        ),
        server=HttpClient(
            url=env.str('URL'),
            port=env.int('PORT'),
            webhook_secret=env.str('WEBHOOK_SECRET')
        ),
        openai=OpenAI(
            token=env.str("OPENAI_TOKEN")
        ),
        redis=RedisStorage(
            host=env.str("REDIS_HOST"),
            port=env.int("REDIS_PORT"),
            password=env.str("REDIS_PASS"),
            redis_enabled=env.bool("REDIS_STORAGE_ENABLE", "false")
        )
    )
