from aiogram import Router
from handlers.user import (employeer, start, profile, change_settings,
                           user_creation, worker, chat, support, done_work)
from handlers.admin import admin



def handle_routers() -> Router:
    router = Router()
    router.include_routers(
        start.router,
        admin.router,
        user_creation.router,
        done_work.router,
        support.router,
        worker.router,
        change_settings.router,
        profile.router,
        employeer.router,
        chat.router
    )
    return router