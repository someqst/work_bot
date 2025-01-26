import asyncio
from loader import dp, bot
from handlers import handle_routers
from utils.set_cmds import set_commands
from utils.schedulers import scheduler




async def main():
    dp.include_routers(handle_routers())
    await set_commands()
    scheduler.start()
    await bot.send_message(539937958, 'Старт начался')
    await dp.start_polling(bot)



asyncio.run(main())
