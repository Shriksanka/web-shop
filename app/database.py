# import sqlite3 as sq
# import uuid
# import os
#
#
# async def db_start():
#     global db, cur
#     db = sq.connect('tg.db')
#     db.row_factory = sq.Row
#     cur = db.cursor()
#     cur.execute("CREATE TABLE IF NOT EXISTS cart("
#                 "cart_id INTEGER PRIMARY KEY AUTOINCREMENT)")
#     cur.execute("CREATE TABLE IF NOT EXISTS accounts("
#                 "id INTEGER PRIMARY KEY AUTOINCREMENT, "
#                 "tg_id INTEGER UNIQUE, "
#                 "id_cart INTEGER,"
#                 "FOREIGN KEY (id_cart) REFERENCES cart(cart_id))")
#     cur.execute("CREATE TABLE IF NOT EXISTS city("
#                 "city_id INTEGER PRIMARY KEY AUTOINCREMENT,"
#                 "name TEXT)")
#     cur.execute("CREATE TABLE IF NOT EXISTS quantity("
#                 "quantity_id INTEGER PRIMARY KEY AUTOINCREMENT,"
#                 "value TEXT)")
#     cur.execute("CREATE TABLE IF NOT EXISTS genre("
#                 "genre_id INTEGER PRIMARY KEY AUTOINCREMENT,"
#                 "name TEXT)")
#     cur.execute("CREATE TABLE IF NOT EXISTS subgenre("
#                 "subgenre_id INTEGER PRIMARY KEY AUTOINCREMENT,"
#                 "name TEXT,"
#                 "description TEXT,"
#                 "photo TEXT,"
#                 "id_genre INTEGER,"
#                 "FOREIGN KEY (id_genre) REFERENCES genre(genre_id))")
#     cur.execute("CREATE TABLE IF NOT EXISTS items("
#                 "item_id INTEGER PRIMARY KEY AUTOINCREMENT, "
#                 "uuid TEXT UNIQUE, "  # Добавлено новое поле uuid
#                 "photo TEXT, "
#                 "location TEXT, "
#                 "id_city INTEGER, "
#                 "id_quantity INTEGER, "
#                 "id_genre INTEGER,"
#                 "id_subgenre INTEGER,"
#                 "FOREIGN KEY (id_city) REFERENCES city(city_id),"
#                 "FOREIGN KEY (id_quantity) REFERENCES quantity(quantity_id),"
#                 "FOREIGN KEY (id_genre) REFERENCES genre(genre_id),"
#                 "FOREIGN KEY (id_subgenre) REFERENCES subgenre(subgenre_id))")
#     cur.execute("CREATE TABLE IF NOT EXISTS cart_items("
#                 "id INTEGER PRIMARY KEY AUTOINCREMENT,"
#                 "id_cart INTEGER,"
#                 "id_item INTEGER,"
#                 "FOREIGN KEY (id_cart) REFERENCES cart(cart_id),"
#                 "FOREIGN KEY (id_item) REFERENCES items(item_id))")
#
#     db.commit()
#
#
# async def add_city(city_name):
#     cur.execute("INSERT INTO city (name) VALUES (?)", (city_name,))
#     db.commit()
#
#
# async def add_quantity(quantity_value):
#     cur.execute("INSERT INTO quantity (value) VALUES (?)", (quantity_value,))
#     db.commit()
#
#
# async def add_genre(genre_name):
#     cur.execute("INSERT INTO genre (name) VALUES (?)", (genre_name,))
#     db.commit()
#
#
# async def add_subgenre(name, description, photo, genre_id):
#     cur.execute(
#         "INSERT INTO subgenre (name, description, photo, id_genre) VALUES (?, ?, ?, ?)",
#         (name, description, photo, genre_id)
#     )
#     db.commit()
#
#
# async def add_item(photo, location, city_id, quantity_id, genre_id, subgenre_id):
#     item_uuid = str(uuid.uuid4())
#     cur.execute(
#         "INSERT INTO items (uuid, photo, location, id_city, id_quantity, id_genre, id_subgenre) "
#         "VALUES (?, ?, ?, ?, ?, ?, ?)",
#         (item_uuid, photo, location, city_id, quantity_id, genre_id, subgenre_id)
#     )
#     db.commit()
#
#
# async def get_all_genres():
#     cur.execute("SELECT * FROM genre")
#     genres = cur.fetchall()
#     return genres
#
#
# async def get_all_cities():
#     cur.execute("SELECT * FROM city")
#     cities = cur.fetchall()
#     return cities
#
#
# async def get_all_quantities():
#     cur.execute("SELECT * FROM quantity")
#     quantities = cur.fetchall()
#     return quantities
#
#
# async def get_all_subgenres():
#     cur.execute("SELECT * FROM subgenre")
#     subgenres = cur.fetchall()
#     return subgenres
#
#
# async def get_all_items():
#     cur.execute("SELECT * FROM items")
#     items = cur.fetchall()
#     return items
#
#
# async def get_item_by_id(item_id):
#     cur.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
#     item = cur.fetchone()
#     return item
#
#
# async def get_genre_by_id(genre_id):
#     cur.execute("SELECT * FROM genre WHERE genre_id = ?", (genre_id,))
#     genre = cur.fetchone()
#     return genre
#
#
# async def get_subgenre_by_id(subgenre_id):
#     cur.execute("SELECT * FROM subgenre WHERE subgenre_id = ?", (subgenre_id,))
#     subgenre = cur.fetchone()
#     return subgenre
#
#
# async def get_items_by_parameters(city_id, genre_id, subgenre_id, quantity_id):
#     cur.execute("SELECT * FROM items WHERE id_city = ? AND id_genre =  AND id_subgenre = ? AND id_quantity = ?",
#                 (city_id, genre_id, subgenre_id, quantity_id))
#     items = cur.fetchall()
#     return items
#
#
# async def get_available_genres_by_city(city_id):
#     cur.execute(
#         "SELECT DISTINCT g.genre_id, g.name "
#         "FROM genre AS g "
#         "JOIN subgenre AS s ON g.genre_id = s.id_genre "
#         "JOIN items AS i ON s.subgenre_id = i.id_subgenre "
#         "WHERE i.id_city = ?",
#         (city_id, )
#     )
#     genres = cur.fetchall()
#     return genres
#
#
# async def get_available_subgenres_by_genre_and_city(genre_id, city_id):
#     cur.execute(
#         "SELECT subgenre_id, name FROM subgenre "
#         "WHERE id_genre = ? AND subgenre_id IN (SELECT id_subgenre FROM items WHERE id_city = ?)",
#         (genre_id, city_id)
#     )
#     subgenres = cur.fetchall()
#     return subgenres
#
#
# async def get_available_quantities_by_subgenre_genre_and_city(subgenre_id, genre_id, city_id):
#     cur.execute(
#         "SELECT DISTINCT quantity.value, quantity.quantity_id "
#         "FROM items "
#         "INNER JOIN quantity ON items.id_quantity = quantity.quantity_id "
#         "WHERE items.id_genre = ? AND items.id_subgenre = ? AND items.id_city = ?",
#         (genre_id, subgenre_id, city_id)
#     )
#     quantities = cur.fetchall()
#     return quantities
#
#
# async def get_items_by_params(city_id, genre_id, subgenre_id, quantity_id):
#     cur.execute(
#         "SELECT * FROM items "
#         "WHERE id_city = ? AND id_genre = ? AND id_subgenre = ? AND id_quantity = ?",
#         (city_id, genre_id, subgenre_id, quantity_id)
#     )
#     items = cur.fetchall()
#     return items

import psycopg2
import os


async def db_start():
    global conn, cur
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS cart ("
                "cart_id SERIAL PRIMARY KEY)")
    cur.execute("CREATE TABLE IF NOT EXISTS accounts ("
                "id SERIAL PRIMARY KEY, "
                "tg_id INTEGER UNIQUE, "
                "id_cart INTEGER REFERENCES cart(cart_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS city ("
                "city_id SERIAL PRIMARY KEY, "
                "name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS quantity ("
                "quantity_id SERIAL PRIMARY KEY, "
                "value TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS genre ("
                "genre_id SERIAL PRIMARY KEY, "
                "name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS subgenre ("
                "subgenre_id SERIAL PRIMARY KEY, "
                "name TEXT, "
                "description TEXT, "
                "photo TEXT, "
                "id_genre INTEGER REFERENCES genre(genre_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS items ("
                "item_id SERIAL PRIMARY KEY, "
                "uuid UUID DEFAULT uuid_generate_v4(), "
                "photo TEXT, "
                "location TEXT, "
                "id_city INTEGER REFERENCES city(city_id), "
                "id_quantity INTEGER REFERENCES quantity(quantity_id), "
                "id_genre INTEGER REFERENCES genre(genre_id), "
                "id_subgenre INTEGER REFERENCES subgenre(subgenre_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS cart_items ("
                "id SERIAL PRIMARY KEY, "
                "id_cart INTEGER REFERENCES cart(cart_id), "
                "id_item INTEGER REFERENCES items(item_id))")

    conn.commit()


async def add_city(city_name):
    cur.execute("INSERT INTO city (name) VALUES (%s)", (city_name,))
    conn.commit()


async def add_quantity(quantity_value):
    cur.execute("INSERT INTO quantity (value) VALUES (%s)", (quantity_value,))
    conn.commit()


async def add_genre(genre_name):
    cur.execute("INSERT INTO genre (name) VALUES (%s)", (genre_name,))
    conn.commit()


async def add_subgenre(name, description, photo, genre_id):
    cur.execute(
        "INSERT INTO subgenre (name, description, photo, id_genre) VALUES (%s, %s, %s, %s)",
        (name, description, photo, genre_id)
    )
    conn.commit()


async def add_item(photo, location, city_id, quantity_id, genre_id, subgenre_id):
    cur.execute(
        "INSERT INTO items (photo, location, id_city, id_quantity, id_genre, id_subgenre) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (photo, location, city_id, quantity_id, genre_id, subgenre_id)
    )
    conn.commit()


async def get_all_genres():
    cur.execute("SELECT * FROM genre")
    genres = cur.fetchall()
    return genres


async def get_all_cities():
    cur.execute("SELECT * FROM city")
    cities = cur.fetchall()
    return cities


async def get_all_quantities():
    cur.execute("SELECT * FROM quantity")
    quantities = cur.fetchall()
    return quantities


async def get_all_subgenres():
    cur.execute("SELECT * FROM subgenre")
    subgenres = cur.fetchall()
    return subgenres


async def get_all_items():
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    return items


async def get_item_by_id(item_id):
    cur.execute("SELECT * FROM items WHERE item_id = %s", (item_id,))
    item = cur.fetchone()
    return item


async def get_genre_by_id(genre_id):
    cur.execute("SELECT * FROM genre WHERE genre_id = %s", (genre_id,))
    genre = cur.fetchone()
    return genre


async def get_subgenre_by_id(subgenre_id):
    cur.execute("SELECT * FROM subgenre WHERE subgenre_id = %s", (subgenre_id,))
    subgenre = cur.fetchone()
    return subgenre


async def get_items_by_parameters(city_id, genre_id, subgenre_id, quantity_id):
    cur.execute(
        "SELECT * FROM items WHERE id_city = %s AND id_genre = %s AND id_subgenre = %s AND id_quantity = %s",
        (city_id, genre_id, subgenre_id, quantity_id)
    )
    items = cur.fetchall()
    return items


async def get_available_genres_by_city(city_id):
    cur.execute(
        "SELECT DISTINCT g.genre_id, g.name "
        "FROM genre AS g "
        "JOIN subgenre AS s ON g.genre_id = s.id_genre "
        "JOIN items AS i ON s.subgenre_id = i.id_subgenre "
        "WHERE i.id_city = %s",
        (city_id, )
    )
    genres = cur.fetchall()
    return genres


async def get_available_subgenres_by_genre_and_city(genre_id, city_id):
    cur.execute(
        "SELECT subgenre_id, name FROM subgenre "
        "WHERE id_genre = %s AND subgenre_id IN (SELECT id_subgenre FROM items WHERE id_city = %s)",
        (genre_id, city_id)
    )
    subgenres = cur.fetchall()
    return subgenres


async def get_available_quantities_by_subgenre_genre_and_city(subgenre_id, genre_id, city_id):
    cur.execute(
        "SELECT DISTINCT quantity.value, quantity.quantity_id "
        "FROM items "
        "INNER JOIN quantity ON items.id_quantity = quantity.quantity_id "
        "WHERE items.id_genre = %s AND items.id_subgenre = %s AND items.id_city = %s",
        (genre_id, subgenre_id, city_id)
    )
    quantities = cur.fetchall()
    return quantities


async def get_items_by_params(city_id, genre_id, subgenre_id, quantity_id):
    cur.execute(
        "SELECT * FROM items "
        "WHERE id_city = %s AND id_genre = %s AND id_subgenre = %s AND id_quantity = %s",
        (city_id, genre_id, subgenre_id, quantity_id)
    )
    items = cur.fetchall()
    return items
