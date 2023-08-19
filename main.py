from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from app.states import AddCity, AddQuantity, AddGenre, AddSubgenre, AddItem, ViewItem
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
async def add_item(callback_query: types.CallbackQuery):
    await callback_query.answer("Отправьте фото товара:")
    await AddItem.WaitingForPhoto.set()


@dp.message_handler(content_types=['photo'], state=AddItem.WaitingForPhoto)
async def add_item_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id

    await AddItem.next()
    await message.answer("Отправьте локацию товара")


@dp.message_handler(state=AddItem.WaitingForLocation)
async def add_item_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['location'] = message.text

    await AddItem.next()
    city_inline_menu = await kb.build_city_inline_menu()
    await message.answer("Выбери город", reply_markup=city_inline_menu)


@dp.callback_query_handler(state=AddItem.WaitingForCity)
async def process_city_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['city_id'] = callback_query.data

    await AddItem.next()
    quantity_inline_menu = await kb.build_quantity_inline_menu()
    await callback_query.answer('Выбери количество')
    await callback_query.message.edit_reply_markup(reply_markup=quantity_inline_menu)


@dp.callback_query_handler(state=AddItem.WaitingForQuantity)
async def process_quantity_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['quantity_id'] = callback_query.data

    await AddItem.next()
    genre_inline_menu = await kb.build_genre_inline_menu()
    await callback_query.answer('Выбери жанр')
    await callback_query.message.edit_reply_markup(reply_markup=genre_inline_menu)


@dp.callback_query_handler(state=AddItem.WaitingForGenre)
async def process_genre_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['genre_id'] = callback_query.data

    await AddItem.next()
    subgenre_inline_menu = await kb.build_subgenre_inline_menu()
    await callback_query.answer('Выбери поджанр')
    await callback_query.message.edit_reply_markup(reply_markup=subgenre_inline_menu)


@dp.callback_query_handler(state=AddItem.WaitingForSubgenre)
async def process_subgenre_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['subgenre_id'] = callback_query.data
        await db.add_item(
            data['photo'],
            data['location'],
            data['city_id'],
            data['quantity_id'],
            data['genre_id'],
            data['subgenre_id']
        )
    await state.finish()
    await callback_query.answer('Предмет добавлен!')


@dp.callback_query_handler(text="view_item")
async def view_city(callback_query: types.CallbackQuery):
    cities_inline_menu = await kb.build_city_inline_menu()
    await callback_query.answer("Выберите город")
    await callback_query.message.edit_reply_markup(reply_markup=cities_inline_menu)
    await ViewItem.WaitingForCity.set()


@dp.callback_query_handler(state=ViewItem.WaitingForCity)
async def process_city_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['city_id'] = callback_query.data

    await ViewItem.next()
    available_genres = await db.get_available_genres_by_city(data['city_id'])
    genre_inline_menu = InlineKeyboardMarkup(row_width=2)
    for genre in available_genres:
        genre_inline_menu.insert(
            InlineKeyboardButton(genre['name'], callback_data=f"view_genre_{genre['genre_id']}")
        )
    await callback_query.answer("Выберите жанр")
    await callback_query.message.edit_reply_markup(reply_markup=genre_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_genre_"),
                           state=ViewItem.WaitingForGenre)
async def process_genre_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['genre_id'] = callback_query.data.split("_")[2]

    await ViewItem.next()
    available_subgenres = await db.get_available_subgenres_by_genre_and_city(data['genre_id'], data['city_id'])
    subgenre_inline_menu = InlineKeyboardMarkup(row_width=2)
    for subgenre in available_subgenres:
        subgenre_inline_menu.insert(
            InlineKeyboardButton(subgenre['name'], callback_data=f"view_subgenre_{subgenre['subgenre_id']}")
        )
    await callback_query.answer("Выберите поджанр")
    await callback_query.message.edit_reply_markup(reply_markup=subgenre_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_subgenre_"),
                           state=ViewItem.WaitingForSubgenre)
async def process_subgenre_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['subgenre_id'] = callback_query.data.split("_")[2]

    await ViewItem.next()

    subgenre_card = await db.get_subgenre_by_id(data['subgenre_id'])
    await callback_query.message.answer_photo(photo=subgenre_card['photo'])
    await callback_query.message.answer(f"Имя: {subgenre_card['name']}")
    await callback_query.message.answer(f"Описание: {subgenre_card['description']}")

    available_quantities = await db.get_available_quantities_by_subgenre_genre_and_city(data['subgenre_id'],
                                                                                        data['genre_id'],
                                                                                        data['city_id'])
    quantity_inline_menu = InlineKeyboardMarkup(row_width=2)
    for quantity in available_quantities:
        quantity_inline_menu.insert(
            InlineKeyboardButton(quantity['value'], callback_data=f"view_quantity_{quantity['quantity_id']}")
        )

    await callback_query.answer("Выберите количество")
    await callback_query.message.edit_reply_markup(reply_markup=quantity_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_quantity_"),
                           state=ViewItem.WaitingForQuantity)
async def process_quantity_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['quantity_id'] = callback_query.data.split("_")[2]

    await ViewItem.next()
    available_items = await db.get_items_by_params(data['city_id'], data['genre_id'], data['subgenre_id'],
                                                   data['quantity_id'])
    items_inline_menu = InlineKeyboardMarkup(row_width=2)
    for item in available_items:
        items_inline_menu.insert(
            InlineKeyboardButton(f"Item ID: {item['item_id']} | UUID: {item['uuid']}",
                                 callback_data=f"view_item_{item['item_id']}")
        )
    await callback_query.answer("Выберите предмет из списка")
    await callback_query.message.edit_reply_markup(reply_markup=items_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_item_"),
                           state=ViewItem.WaitingForItem)
async def process_item_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    item_id = callback_query.data.split("_")[2]
    item = await db.get_item_by_id(item_id)

    await callback_query.message.answer_photo(photo=item['photo'])
    await callback_query.message.answer(f"Location: {item['location']}")
    await callback_query.answer('Просмотрен предмет')

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
