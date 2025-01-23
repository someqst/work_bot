import asyncio
from loader import dp, bot
from handlers import handle_routers




async def main():
    dp.include_routers(handle_routers())
    await bot.send_message(539937958, 'Старт начался')
    await dp.start_polling(bot)



asyncio.run(main())
