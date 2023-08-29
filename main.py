import hashlib
import time
import hmac
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from app.states import AddCity, AddQuantity, AddGenre, AddSubgenre, AddItem, ViewItem, AddPrice, ShopMenu
from app import keyboards as kb
from app import database as db
from dotenv import load_dotenv
import os
import json
import requests
from urllib.parse import urlencode

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
    quantity_inline_menu = await kb.build_quantities_inline_menu()
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
            InlineKeyboardButton(genre[1], callback_data=f"view_genre_{genre[0]}")
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
            InlineKeyboardButton(subgenre[1], callback_data=f"view_subgenre_{subgenre[0]}")
        )
    await callback_query.answer("Выберите поджанр")
    await callback_query.message.edit_reply_markup(reply_markup=subgenre_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_subgenre_"),
                           state=ViewItem.WaitingForSubgenre)
async def process_subgenre_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    subgenre_id = callback_query.data.split("_")[2]
    async with state.proxy() as data:
        data['subgenre_id'] = subgenre_id

    quantity_inline_menu = await kb.build_quantity_inline_menu(subgenre_id)
    await callback_query.message.edit_reply_markup(reply_markup=quantity_inline_menu)
    await callback_query.answer("Выберите количество")
    await ViewItem.WaitingForQuantity.set()


# @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_subgenre_"),
#                            state=ViewItem.WaitingForSubgenre)
# async def process_subgenre_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
#     async with state.proxy() as data:
#         data['subgenre_id'] = callback_query.data.split("_")[2]
#
#     await ViewItem.next()
#
#     subgenre_card = await db.get_subgenre_by_id(data['subgenre_id'])
#     await callback_query.message.answer_photo(photo=subgenre_card[3])
#     await callback_query.message.answer(f"Имя: {subgenre_card[1]}")
#     await callback_query.message.answer(f"Описание: {subgenre_card[2]}")
#
#     available_quantities = await db.get_available_quantities_by_subgenre_genre_and_city(data['subgenre_id'],
#                                                                                         data['genre_id'],
#                                                                                         data['city_id'])
#     quantity_inline_menu = InlineKeyboardMarkup(row_width=2)
#     for quantity in available_quantities:
#         quantity_inline_menu.insert(
#             InlineKeyboardButton(quantity[1], callback_data=f"view_quantity_{quantity[0]}")
#         )
#
#     await callback_query.answer("Выберите количество")
#     await callback_query.message.edit_reply_markup(reply_markup=quantity_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_quantity_"),
                           state=ViewItem.WaitingForQuantity)
async def process_quantity_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    subgenre_id = callback_query.data.split("_")[1]
    quantity_id = callback_query.data.split("_")[2]
    async with state.proxy() as data:
        data['quantity_id'] = quantity_id

    subgenre_price = await db.get_subgenre_price(subgenre_id, quantity_id)
    await ViewItem.next()

    subgenre_card = await db.get_subgenre_by_id(subgenre_id)
    await callback_query.message.answer_photo(photo=subgenre_card[3])
    await callback_query.message.answer(f"Имя: {subgenre_card[1]}")
    await callback_query.message.answer(f"Описание: {subgenre_card[2]}")
    await callback_query.message.answer(f"Цена: {subgenre_price} (PLN)")


@dp.callback_query_handler(text="add_price")
async def admin_add_panel(callback_query: types.CallbackQuery):
    subgenres = await db.get_all_subgenres()
    subgenre_inline_menu = InlineKeyboardMarkup(row_width=1)
    for subgenre in subgenres:
        subgenre_id = subgenre[0]
        subgenre_name = subgenre[1]
        subgenre_inline_menu.insert(
            InlineKeyboardButton(subgenre_name, callback_data=f"add_price_{subgenre_id}")
        )
    await callback_query.answer("Выберите поджанр, для которого хотите добавить цену")
    await callback_query.message.edit_reply_markup(reply_markup=subgenre_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("add_price_"))
async def process_subgenre_for_price(callback_query: types.CallbackQuery, state: FSMContext):
    subgenre_id = callback_query.data.split("_")[2]

    async with state.proxy() as data:
        data['subgenre_id_for_price'] = subgenre_id

    await AddPrice.WaitingForQuantityAndPrice.set()

    await callback_query.answer("Выберите количество и введите цену:")
    quantity_inline_menu = await kb.build_quantity_inline_menu(subgenre_id)
    await callback_query.message.edit_reply_markup(reply_markup=quantity_inline_menu)


@dp.callback_query_handler(state=AddPrice.WaitingForQuantityAndPrice)
async def process_quantity_and_price(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['quantity_id_for_price'] = callback_query.data

    await AddPrice.WaitingForPrice.set()
    await callback_query.answer("Введите цену:")


@dp.message_handler(state=AddPrice.WaitingForPrice)
async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        subgenre_id = data['subgenre_id_for_price']
        quantity_id = data['quantity_id_for_price']
        price = message.text

    await db.add_subgenre_price(subgenre_id, quantity_id, price)
    await state.finish()
    await message.reply("Цена успешно добавлена!")


# async def process_quantity_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
#     async with state.proxy() as data:
#         data['quantity_id'] = callback_query.data.split("_")[2]
#
#     await ViewItem.next()
#     available_items = await db.get_items_by_params(data['city_id'], data['genre_id'], data['subgenre_id'],
#                                                    data['quantity_id'])
#     items_inline_menu = InlineKeyboardMarkup(row_width=2)
#     for item in available_items:
#         items_inline_menu.insert(
#             InlineKeyboardButton(f"Item ID: {item[0]} | UUID: {item[1]}",
#                                  callback_data=f"view_item_{item[0]}")
#         )
#     await callback_query.answer("Выберите предмет из списка")
#     await callback_query.message.edit_reply_markup(reply_markup=items_inline_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("view_item_"),
                           state=ViewItem.WaitingForItem)
async def process_item_choice_view(callback_query: types.CallbackQuery, state: FSMContext):
    item_id = callback_query.data.split("_")[2]
    item = await db.get_item_by_id(item_id)

    await callback_query.message.answer_photo(photo=item[2])
    await callback_query.message.answer(f"Location: {item[3]}")
    await callback_query.answer('Просмотрен предмет')

    await state.finish()


@dp.message_handler(lambda message: message.text == 'Магазин')
async def shop_menu(message: types.Message):
    cities_inline_menu = await kb.build_city_inline_menu()
    await message.answer("Выберите город", reply_markup=cities_inline_menu)
    await ShopMenu.WaitingForCity.set()


@dp.callback_query_handler(state=ShopMenu.WaitingForCity)
async def process_city_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['city_id'] = callback_query.data

    genres_inline_menu = await kb.build_genre_inline_menu()
    await callback_query.answer("Выберите жанр")
    await callback_query.message.edit_reply_markup(reply_markup=genres_inline_menu)
    await ShopMenu.WaitingForGenre.set()


@dp.callback_query_handler(state=ShopMenu.WaitingForGenre)
async def process_genre_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['genre_id'] = callback_query.data

    subgnres_inline_menu = await kb.build_subgenre_inline_menu()
    await callback_query.answer("Выберите поджанр")
    await callback_query.message.edit_reply_markup(reply_markup=subgnres_inline_menu)
    await ShopMenu.WaitingForSubgenre.set()


@dp.callback_query_handler(state=ShopMenu.WaitingForSubgenre)
async def process_subgenre_choice(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['subgenre_id'] = callback_query.data

    # Получаем информацию о поджанре из базы данных
    subgenre_info = await db.get_subgenre_by_id(data['subgenre_id'])

    # Отправляем информацию о поджанре и его цене
    await callback_query.message.answer_photo(photo=subgenre_info[3])
    await callback_query.message.answer(f"Имя: {subgenre_info[1]}")
    await callback_query.message.answer(f"Описание: {subgenre_info[2]}")

    quantity_inline_menu = await kb.build_quantity_inline_menu(subgenre_info[0])  # Передаем ID поджанра
    await callback_query.message.answer("Выберите количество", reply_markup=quantity_inline_menu)

    await ShopMenu.WaitingForQuantity.set()


BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BTC_TO_PLN_SYMBOL = "BTCPLN"


def generate_unique_address():
    timestamp = int(time.time() * 1000)

    query_params = {
        "timestamp": timestamp,
        "recvWindow": 5000,
        "coin": "BTC"
    }

    query_string = urlencode(query_params)

    signature = hmac.new(os.getenv('API_SECRET').encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    payload = {
        "timestamp": timestamp,
        "recvWindow": 5000,
        "signature": signature,
        "coin": "BTC"
    }

    response = requests.get("https://api.binance.com/sapi/v1/capital/deposit/address",
                             params=payload, headers={"X-MBX-APIKEY": os.getenv('API_KEY')})

    if response.status_code == 200:
        address = response.json().get("address")
        print("Address generated successfully:", address)
    else:
        print("Error generating address. Response:", response.text)
        address = None

    return address


@dp.callback_query_handler(state=ShopMenu.WaitingForQuantity)
async def process_quantity_choice(callback_query: types.CallbackQuery, state: FSMContext):
    quantity_id = callback_query.data

    async with state.proxy() as data:
        subgenre_id = data['subgenre_id']
        data['quantity_id'] = quantity_id

    # Получаем цену для выбранного поджанра и количества
    subgenre_price_pln = await db.get_subgenre_price(subgenre_id, quantity_id)

    # Получаем текущий курс BTC к PLN с Binance API
    response = requests.get(f"{BINANCE_API_URL}?symbol={BTC_TO_PLN_SYMBOL}")
    btc_to_pln_price = float(response.json()["price"])

    # Рассчитываем цену в BTC
    subgenre_price_btc = float(subgenre_price_pln) / btc_to_pln_price

    # Отправляем сообщение с ценой
    message = (
        f"Цена для данного Поджанра за Такое Количество: {subgenre_price_pln} PLN\n"
        f"Цена в BTC по текущему курсу: {subgenre_price_btc:.8f} BTC"
    )

    # Создаем клавиатуру с кнопкой "Оплатить криптой"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Оплатить криптой", callback_data="pay_with_crypto")]
    ])

    await callback_query.message.answer(message, reply_markup=keyboard)

    await ShopMenu.WaitingForPaymentAddress.set()
    async with state.proxy() as data:
        data['subgenre_price_btc'] = subgenre_price_btc


@dp.callback_query_handler(text="pay_with_crypto", state=ShopMenu.WaitingForPaymentAddress)
async def generate_payment_address(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        subgenre_price_btc = data['subgenre_price_btc']
        subgenre_id = data['subgenre_id']
        quantity_id = data['quantity_id']

    # Генерируем уникальный адрес для оплаты
    payment_address = generate_unique_address()

    # Сохраняем уникальный адрес в базе данных для проверки оплаты
    await db.save_payment_address(subgenre_id, quantity_id, payment_address)

    # Отправляем адрес пользователю
    await callback_query.message.answer(f"Для оплаты в криптовалюте используйте следующий адрес:\n{payment_address}")

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)