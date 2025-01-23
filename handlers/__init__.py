from aiogram import Router
from handlers.user import start, job_create, profile



def handle_routers() -> Router:
    router = Router()
    router.include_routers(
        start.router,
        profile.router,
        job_create.router
    )
    return router