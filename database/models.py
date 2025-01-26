from pytz import timezone
from datetime import datetime
from sqlalchemy import Text, DateTime, BigInteger, UUID, ForeignKey
from sqlalchemy.orm import mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id = mapped_column(BigInteger, primary_key=True, unique=True)
    username = mapped_column(Text)
    registered_at = mapped_column(DateTime, default=datetime.now(timezone('Europe/Moscow')).replace(tzinfo=None))
    last_usage = mapped_column(DateTime, default=datetime.now(timezone('Europe/Moscow')).replace(tzinfo=None))
    role = mapped_column(Text, default='worker')
    location = mapped_column(Text)
    about = mapped_column(Text)
    done_works = mapped_column(BigInteger, default=0)
    balance_earned = mapped_column(BigInteger, default=0)
    balance_deposit = mapped_column(BigInteger, default=0)


class Work(Base):
    __tablename__ = 'work'
    id = mapped_column(UUID, primary_key=True, unique=True)
    owner = mapped_column(ForeignKey(User.id))
    title = mapped_column(Text)
    description = mapped_column(Text)
    status = mapped_column(Text, default='opened')
    work_time = mapped_column(BigInteger, default=0)
    price = mapped_column(BigInteger, default=0)
    location = mapped_column(Text)
    creation_time = mapped_column(DateTime, default=datetime.now(timezone('Europe/Moscow')).replace(tzinfo=None))


class WorkProcess(Base):
    __tablename__ = 'workprocess'
    id = mapped_column(ForeignKey(Work.id), primary_key=True)
    title = mapped_column(Text)
    end_time = mapped_column(DateTime)
    price = mapped_column(BigInteger)
    worker = mapped_column(ForeignKey(User.id))
    owner = mapped_column(ForeignKey(User.id))


class Chat(Base):
    __tablename__ = 'chat'
    id = mapped_column(BigInteger, primary_key=True)
    chat_with = mapped_column(BigInteger)