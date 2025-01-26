from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.delete_expired_works import delete_works
from utils.reminder import remaind_about_work_1hour, remaind_about_work_30mins



scheduler = AsyncIOScheduler()
scheduler.add_job(delete_works, 'cron', minute=53)
scheduler.add_job(remaind_about_work_1hour, 'cron', minute=10)
scheduler.add_job(remaind_about_work_30mins, 'cron', minute='*')