from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    user_redis: bool


@dataclass
class Db_Config:
    host: str
    password: str
    usr: str
    Database: str


@dataclass
class Miscellaneous:
    other_paraments: str = None


@dataclass
class Config_py:
    tg_bot: TgBot
    db: Db_Config
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path=path)
    return Config_py(
        tg_bot=TgBot(token=env.str('BOT_TOKEN'),
                     admin_ids=list(map(int, env.list('ADMINS'))),
                     user_redis=env.bool('USER_REDIS')),
        db=Db_Config(host=env.str('DB_HOST'),
                     password=env.str('DB_PASSWORD'),
                     usr=env.str('DB_USER'),
                     Database=env.str('DATA_BASE')),
        misc=Miscellaneous())
