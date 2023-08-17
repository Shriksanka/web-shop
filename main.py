from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from app.states import AddCity, AddQuantity, AddGenre, AddSubgenre
from app import keyboards as kb
from app import database as db
from dotenv import load_dotenv
import os
import json

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)


async def on_startup(_):
    await db.db_start()
    print('Бот успешно запущен!')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    if str(user_id) == os.getenv('ADMIN_ID'):
        markup = kb.link_web_with_admin
    else:
        markup = kb.link_web
    await message.answer('Привет мой друг', reply_markup=markup)


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    res = json.loads(message.web_app_data.data)
    await message.answer(f'Name: {res["name"]}. Email: {res["email"]}. Phone: {res["phone"]}')


@dp.message_handler(lambda message: message.text == 'Админ-панель', user_id=os.getenv('ADMIN_ID'))
async def admin_panel(message: types.Message):
    await message.answer('Вы в админ панели', reply_markup=kb.admin_inline_menu)


@dp.callback_query_handler(text="add_city")
async def add_city(callback_query: types.CallbackQuery):
    await callback_query.answer("Введите название города")
    await AddCity.WaitingForCity.set()


@dp.message_handler(state=AddCity.WaitingForCity)
async def process_city_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city_name'] = message.text

        await db.add_city(data['city_name'])

    await state.finish()
    await message.reply(f"Город {data['city_name']} добавлен!")


@dp.callback_query_handler(text="add_quantity")
async def add_quantity(callback_query: types.CallbackQuery):
    await callback_query.answer("Введите количество")
    await AddQuantity.WaitingForQuantity.set()


@dp.message_handler(state=AddQuantity.WaitingForQuantity)
async def process_quantity(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity_value'] = message.text

        await db.add_quantity(data['quantity_value'])

    await state.finish()
    await message.reply(f"Количество {data['quantity_value']} добавлено!")


@dp.callback_query_handler(text="add_genre")
async def add_genre(callback_query: types.CallbackQuery):
    await callback_query.answer("Введите жанр")
    await AddGenre.WaitingForGenre.set()


@dp.message_handler(state=AddGenre.WaitingForGenre)
async def process_quantity(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['genre_name'] = message.text

        await db.add_genre(data['genre_name'])

    await state.finish()
    await message.reply(f"Жанр {data['genre_name']} добавлен!")


@dp.callback_query_handler(text="add_subgenre")
async def add_city(callback_query: types.CallbackQuery):
    await callback_query.answer("Введите имя поджанра")
    await AddSubgenre.WaitingForSubgenreName.set()


@dp.message_handler(state=AddSubgenre.WaitingForSubgenreName)
async def process_subgenre_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['subgenre_name'] = message.text

    await AddSubgenre.next()
    await message.answer("Введите описание поджанра")


@dp.message_handler(state=AddSubgenre.WaitingForSubgenreDescription)
async def process_subgenre_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['subgenre_description'] = message.text

    await AddSubgenre.next()
    await message.answer("Отправьте фото поджанра")


@dp.message_handler(content_types=['photo'], state=AddSubgenre.WaitingForSubgenrePhoto)
async def process_subgenre_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['subgenre_photo'] = message.photo[0].file_id
    await AddSubgenre.next()
    genre_inline_menu = await kb.build_genre_inline_menu()
    await message.answer("Выберите жанр", reply_markup=genre_inline_menu)


@dp.callback_query_handler(state=AddSubgenre.WaitingForGenreChoice)
async def process_genre_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['genre_id'] = callback_query.data
        await db.add_subgenre(
            data['subgenre_name'],
            data['subgenre_description'],
            data['subgenre_photo'],
            data['genre_id']
        )
    await state.finish()
    await callback_query.answer('Поджанр добавлен!')


@dp.callback_query_handler(text="add_item")
async def add_city(callback_query: types.CallbackQuery):
    await callback_query.answer("Добавить товар")


@dp.callback_query_handler(text="view_item")
async def add_city(callback_query: types.CallbackQuery):
    await callback_query.answer("Просмотр товара")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
