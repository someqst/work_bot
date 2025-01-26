from uuid import uuid4
from pytz import timezone
from datetime import datetime
from database.models import User, Work, WorkProcess, Chat
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from data.config import settings
from sqlalchemy import select, update, delete, insert, func, or_, and_




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
    async def create_user(cls, user_id, username, location = None, role = 'worker', about = None, session: AsyncSession = None):
        user = User(id = user_id, username = username, location = location, role = role, about = about)
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
    

    @classmethod
    @connection
    async def change_user_location(cls, user_id, location, session: AsyncSession = None):
        await session.execute(update(User).where(User.id == user_id).values(location = location))
        await session.commit()
    

    @classmethod
    @connection
    async def change_user_role(cls, user_id, role, session: AsyncSession = None):
        await session.execute(update(User).where(User.id == user_id).values(role = role))
        await session.commit()

    
    @classmethod
    @connection
    async def change_user_about(cls, user_id, about, session: AsyncSession = None):
        await session.execute(update(User).where(User.id == user_id).values(about = about))
        await session.commit()

    
    @classmethod
    @connection
    async def set_work_status(cls, work_id, status, session: AsyncSession = None):
        await session.execute(update(Work).where(Work.id == work_id).values(status = status))
        await session.commit()


    @classmethod
    @connection
    async def select_expired_works(cls, time_now: datetime, session: AsyncSession = None) -> list[WorkProcess] | None:
        return (await session.execute(select(WorkProcess).where(WorkProcess.end_time < time_now))).scalars().all()


    @classmethod
    @connection
    async def delete_expired_work(cls, work_id, session: AsyncSession = None):
        await session.execute(delete(WorkProcess).where(WorkProcess.id == work_id))
        await session.execute(update(Work).where(Work.id == work_id).values(status = 'opened'))
        await session.commit()


    @classmethod
    @connection
    async def create_chat(cls, owner_id, worker_id, session: AsyncSession = None):
        await session.execute(
            delete(Chat).where(
                or_(
                    and_(Chat.id == owner_id, Chat.chat_with == worker_id),
                    and_(Chat.id == worker_id, Chat.chat_with == owner_id),
                    Chat.id == owner_id,
                    Chat.chat_with == owner_id,
                    Chat.id == worker_id,
                    Chat.chat_with == worker_id
                )
            )
        )
        await session.execute(
            insert(Chat).values(id=owner_id, chat_with=worker_id)
        )
        await session.execute(
            insert(Chat).values(id=worker_id, chat_with=owner_id)
        )
        await session.commit()


    @classmethod
    @connection
    async def select_chat_with(cls, user_id, session: AsyncSession = None) -> int:
        return (await session.execute(select(Chat.chat_with).where(Chat.id == user_id))).scalar_one_or_none()


    @classmethod
    @connection
    async def delete_chat(cls, owner_id, session: AsyncSession = None):
        await session.execute(
            delete(Chat).where(
                or_(
                    Chat.id == owner_id,
                    Chat.chat_with == owner_id,
                )
            )
        )
        await session.commit()


    @classmethod
    @connection
    async def close_work(cls, work_id, session: AsyncSession = None) -> int:
        await session.execute(delete(WorkProcess).where(WorkProcess.id == work_id))
        await session.execute(delete(Work).where(Work.id == work_id))
        await session.commit()

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
        session.add(work)
        await session.commit()


    @classmethod
    @connection
    async def select_employeer_jobs(cls, user_id, session: AsyncSession = None):
        return (await session.execute(select(Work).filter(Work.owner == user_id))).scalars().all()
    

    @classmethod
    @connection
    async def get_employeer_deposit(cls, user_id, price, session: AsyncSession = None):
        await session.execute(update(User).where(User.id == user_id).values(balance_deposit = User.balance_deposit - price))
        await session.commit()


# ----------- Worker part ---------------

    @classmethod
    @connection
    async def select_opened_works_by_location(cls, location, session: AsyncSession = None):
        return (await session.execute(select(Work).filter((Work.location.like(location)), Work.status == 'opened').order_by(Work.creation_time))).scalars().all()
    

    @classmethod
    @connection
    async def get_work_by_id(cls, work_id, session: AsyncSession = None) -> Work:
        return (await session.execute(select(Work).where(Work.id == work_id))).scalar_one_or_none()
    

    @classmethod
    @connection
    async def get_work_process_by_id(cls, work_id, session: AsyncSession = None) -> WorkProcess:
        return (await session.execute(select(WorkProcess).where(WorkProcess.id == work_id))).scalar_one_or_none()


    @classmethod
    @connection
    async def create_work_process(cls, work_id, work_title, end_time, work_price, worker_id, owner_id, session: AsyncSession = None):
        work_process = WorkProcess(id = work_id, title = work_title, end_time = end_time, 
                                   price = work_price, worker = worker_id, owner = owner_id)
        session.add(work_process)
        await session.commit()


    @classmethod
    @connection
    async def update_worker_balance(cls, user_id, price, session: AsyncSession = None) -> int:
        await session.execute(update(User).where(User.id == user_id).values(balance_earned = User.balance_earned + price))
        await session.commit()


    @classmethod
    @connection
    async def delete_worker_from_work(cls, user_id, work_id, session: AsyncSession = None):
        await session.execute(delete(WorkProcess).where(WorkProcess.worker == user_id))
        await session.execute(update(Work).where(Work.id == work_id).values(status = 'opened'))
        await session.commit()
