
from os import name
import sqlite3
import aiogram
import asyncio
from aiogram import *
from aiogram.filters import command
from aiogram.types import *
from aiogram.filters import *
from aiogram.types import inline_keyboard_markup
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_CHAT_ID=os.getenv('ADMIN_CHAT_ID')
bot = aiogram.Bot(token=TOKEN)
dp=Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hi")

@dp.message(Command('help'))
async def cmd_help(message:Message):
    await message.answer(f'Ваш chat_id: {message.chat.id}')

async def send_message_async(text:str):
    await bot.send_message(ADMIN_CHAT_ID,text=text)

def send_message(text:str, comment_id):
    async def _send():
        bot_temp=Bot(token=TOKEN)
        await bot_temp.send_message(ADMIN_CHAT_ID, text=text, parse_mode='html',
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подтвердить ✔",callback_data=f"verify_{comment_id}"),
                                                   InlineKeyboardButton(text="Удалить ❌",callback_data=f"delete_{comment_id}")]]))
        await bot_temp.session.close()
    asyncio.run(_send())

@dp.callback_query(F.data.startswith("delete"))
async def verify_comment(callback: CallbackQuery):
    comment_id=int(callback.data[7:])
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gamenews_comment WHERE id = ?;',(comment_id,))
    conn.commit()
    conn.close()
    await callback.answer()
    await callback.message.answer(f"Комментарий с id {comment_id} был удалён")
    await callback.message.edit_reply_markup(reply_markup=None)

@dp.callback_query(F.data.startswith("verify"))
async def verify_comment(callback: CallbackQuery):
    comment_id=int(callback.data[7:])
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('UPDATE gamenews_comment SET verify = 1 WHERE id = ?;',(comment_id,))
    conn.commit()
    conn.close()
    await callback.answer()
    await callback.message.answer(f"Комментарий с id {comment_id} был подтверждён")
    await callback.message.edit_reply_markup(reply_markup=None)
    
async def main():
    await send_message_async("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("БОТ - В С Ё")
    except Exception as e:
        print(f"Ой {e}")