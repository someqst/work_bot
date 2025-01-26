from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.delete_expired_works import delete_works



scheduler = AsyncIOScheduler()
scheduler.add_job(delete_works, 'cron', minute=53)