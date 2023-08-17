import sqlite3 as sq
import uuid
import os


async def db_start():
    global db, cur
    db = sq.connect('tg.db')
    db.row_factory = sq.Row
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS cart("
                "cart_id INTEGER PRIMARY KEY AUTOINCREMENT)")
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER UNIQUE, "
                "id_cart INTEGER,"
                "FOREIGN KEY (id_cart) REFERENCES cart(cart_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS city("
                "city_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS quantity("
                "quantity_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "value TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS genre("
                "genre_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS subgenre("
                "subgenre_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT,"
                "description TEXT,"
                "photo TEXT,"
                "id_genre INTEGER,"
                "FOREIGN KEY (id_genre) REFERENCES genre(genre_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS items("
                "item_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "uuid TEXT UNIQUE, "  # Добавлено новое поле uuid
                "photo TEXT, "
                "location TEXT, "
                "id_city INTEGER, "
                "id_quantity INTEGER, "
                "id_genre INTEGER,"
                "id_subgenre INTEGER,"
                "FOREIGN KEY (id_city) REFERENCES city(city_id),"
                "FOREIGN KEY (id_quantity) REFERENCES quantity(quantity_id),"
                "FOREIGN KEY (id_genre) REFERENCES genre(genre_id),"
                "FOREIGN KEY (id_subgenre) REFERENCES subgenre(subgenre_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS cart_items("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "id_cart INTEGER,"
                "id_item INTEGER,"
                "FOREIGN KEY (id_cart) REFERENCES cart(cart_id),"
                "FOREIGN KEY (id_item) REFERENCES items(item_id))")

    db.commit()


async def add_city(city_name):
    cur.execute("INSERT INTO city (name) VALUES (?)", (city_name,))
    db.commit()


async def add_quantity(quantity_value):
    cur.execute("INSERT INTO quantity (value) VALUES (?)", (quantity_value,))
    db.commit()


async def add_genre(genre_name):
    cur.execute("INSERT INTO genre (name) VALUES (?)", (genre_name,))
    db.commit()


async def add_subgenre(name, description, photo, genre_id):
    print("Adding subgenre:", name, description, photo, genre_id)
    cur.execute(
        "INSERT INTO subgenre (name, description, photo, id_genre) VALUES (?, ?, ?, ?)",
        (name, description, photo, genre_id)
    )
    db.commit()


async def get_all_genres():
    cur.execute("SELECT * FROM genre")
    genres = cur.fetchall()
    return genres
