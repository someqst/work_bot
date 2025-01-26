from aiogram import Router, F
from aiogram.types import Message
from loader import db, bot
from aiogram.filters import Command


router = Router()


@router.message(Command('exit'))
async def exit_cmd(message: Message):
    chat_with = await db.select_chat_with(message.from_user.id)
    await db.delete_chat(message.from_user.id)
    if not chat_with:
        return await message.answer('Собеседник не в чате...')
    await bot.send_message(chat_with, 'Собеседник вышел из чата.')
    await message.answer('Вы успешно вышли из чата')



@router.message(F.text)
async def send_chat_message(message: Message):
    chat_with = await db.select_chat_with(message.from_user.id)

    if not chat_with:
        return await message.answer('Собеседник не в чате...')
    
    try:
        return await bot.send_message(chat_with, message.text, parse_mode='Markdown')
    except:
        return await bot.send_message(chat_with, message.text)
        

@router.message( F.photo)
async def send_chat_photo(message: Message):
    chat_with = await db.select_chat_with(message.from_user.id)

    if not chat_with:
        return await message.answer('Собеседник не в чате...')
    
    try:
        return await bot.send_photo(chat_with, photo=message.photo[-1].file_id, caption=message.caption, parse_mode='Markdown')
    except:
        return await bot.send_photo(chat_with, photo=message.photo[-1].file_id, caption=message.caption)
        

@router.message(F.audio | F.voice | F.video_note | F.video)
async def send_chat_photo(message: Message):
    chat_with = await db.select_chat_with(message.from_user.id)

    if not chat_with:
        return await message.answer('Собеседник не в чате...')

    if message.video:
        await bot.send_video(chat_with, message.video.file_id, caption=message.caption)
    elif message.audio:
        await bot.send_audio(chat_with, message.audio.file_id, caption=message.caption)
    elif message.video_note:
        await bot.send_video_note(chat_with, message.video_note.file_id)
    else:
        await bot.send_voice(chat_with, message.voice.file_id)
