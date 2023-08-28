from aiogram.types.web_app_info import WebAppInfo
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from app import database as db

link_web = ReplyKeyboardMarkup()
link_web.add(KeyboardButton('Открыть веб страницу', web_app=WebAppInfo(url='https://telegram-shop-web-app-7f96b757ecd0.herokuapp.com/')))

link_web_with_admin = ReplyKeyboardMarkup()
link_web_with_admin.add(
    KeyboardButton('Открыть веб страницу', web_app=WebAppInfo(url='https://telegram-shop-web-app-7f96b757ecd0.herokuapp.com/')))
link_web_with_admin.add(KeyboardButton('Админ-панель'))

admin_inline_menu = InlineKeyboardMarkup(row_width=2)
admin_inline_menu.add(
    InlineKeyboardButton("Добавить город", callback_data="add_city"),
    InlineKeyboardButton("Добавить количество", callback_data="add_quantity"),
    InlineKeyboardButton("Добавить жанр", callback_data="add_genre"),
    InlineKeyboardButton("Добавить поджанр", callback_data="add_subgenre"),
    InlineKeyboardButton("Добавить цену", callback_data="add_price"),
    InlineKeyboardButton("Добавить предмет", callback_data="add_item"),
    InlineKeyboardButton("Посмотреть карточку предмета", callback_data="view_item")
)


async def build_genre_inline_menu():
    genre_inline_menu = InlineKeyboardMarkup(row_width=2)
    genres = await db.get_all_genres()
    for genre in genres:
        genre_inline_menu.insert(
            InlineKeyboardButton(genre[1], callback_data=str(genre[0]))
        )
    return genre_inline_menu


async def build_city_inline_menu():
    city_inline_menu = InlineKeyboardMarkup(row_width=2)
    cities = await db.get_all_cities()
    for city in cities:
        city_inline_menu.insert(
            InlineKeyboardButton(city[1], callback_data=str(city[0]))
        )
    return city_inline_menu


async def build_subgenre_inline_menu():
    subgenre_inline_menu = InlineKeyboardMarkup(row_width=2)
    subgenres = await db.get_all_subgenres()
    for subgenre in subgenres:
        subgenre_inline_menu.insert(
            InlineKeyboardButton(subgenre[1], callback_data=str(subgenre[0]))
        )
    return subgenre_inline_menu


async def build_quantity_inline_menu(subgenre_id):
    quantity_inline_menu = InlineKeyboardMarkup(row_width=2)
    quantities = await db.get_all_quantities()
    for quantity in quantities:
        quantity_id = quantity[0]
        quantity_inline_menu.insert(
            InlineKeyboardButton(quantity[1], callback_data=str(quantity[0]))
        )
    return quantity_inline_menu


async def build_quantities_inline_menu():
    quantity_inline_menu = InlineKeyboardMarkup(row_width=2)
    quantities = await db.get_all_quantities()
    for quantity in quantities:
        quantity_inline_menu.insert(
            InlineKeyboardButton(quantity[1], callback_data=str(quantity[0]))
        )
    return quantity_inline_menu
