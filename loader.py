from database.core import DataBase
from aiogram import Dispatcher, Bot
from redis.asyncio import StrictRedis
from aiogram.fsm.storage.redis import RedisStorage
from data.config import settings


db = DataBase()
dp = Dispatcher(storage=RedisStorage(StrictRedis(host='192.168.1.180', db=4)))
bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
