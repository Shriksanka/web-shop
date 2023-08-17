from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo

bot = Bot('6543405819:AAFUaqHH9z8Q4jhOp1V2iWI6JQG7ZOE-i2A')
dp = Dispatcher(bot)


async def on_startup(_):
    print('Бот успешно запущен!')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Открыть веб страницу', web_app=WebAppInfo(url='https://shriksanka.github.io/web-shop/')))
    await message.answer('Привет мой друг', reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)