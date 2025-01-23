from uuid import uuid4
from pytz import timezone
from datetime import datetime
from database.models import User, Work, WorkProcess
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from data.config import settings
from sqlalchemy import select, update, delete, insert, func




engine = create_async_engine(url=settings.DB_URI.get_secret_value())
async_session_maker = async_sessionmaker(engine)

def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await func(*args, **kwargs, session=session)
            except Exception as e:
                print(e)
                await session.rollback()
                raise e
            finally:
                await session.close()
    return wrapper


class DataBase:

    @classmethod
    @connection
    async def create_user(cls, user_id, username, session: AsyncSession = None):
        user = User(id = user_id, username = username)
        await session.merge(user)
        return await session.commit()
    

    @classmethod
    @connection
    async def get_user(cls, user_id, session: AsyncSession = None) -> User:
        return (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    

    @classmethod
    @connection
    async def get_user_ads(cls, user_id, session: AsyncSession = None) -> Work:
        return (await session.execute(select(Work).where(Work.owner == user_id))).scalars().all()
    
#  ------------- Employeer part --------------

    @classmethod
    @connection
    async def create_work(cls, owner: int, location: str, work_time: int, price: int,
                          title: str, description: str, session: AsyncSession = None):
        work = Work(id = str(uuid4()),
                    owner = owner,
                    location = location,
                    status = 'opened',
                    work_time = work_time,
                    price = price,
                    title = title,
                    description = description,
                    creation_time = datetime.now(timezone('Europe/Moscow')).replace(tzinfo=None))
        await session.add(work)
        await session.commit()


    @classmethod
    @connection
    async def select_employeer_jobs(cls, user_id, session: AsyncSession = None):
        return (await session.execute(select(Work).filter(Work.owner == user_id))).scalars().all()


    @classmethod
    @connection
    async def get_job(cls):
        ...
