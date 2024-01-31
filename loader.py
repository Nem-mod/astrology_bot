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


@dataclass
class Config:
    bot: TelegramBot
    server: HttpClient


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        bot=TelegramBot(
            token=env.str("BOT_TOKEN"),
        ),
        server=HttpClient(
            url=env.str('URL'),
            port=env.int('PORT')
        )
    )
