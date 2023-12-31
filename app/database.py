import psycopg2
import os
import asyncpg


async def db_start():
    global conn, cur
    database_url = os.getenv('DATABASE_URL')# os.environ['DATABASE_URL']
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
                "uuid UUID DEFAULT gen_random_uuid(), "
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
    cur.execute("CREATE TABLE IF NOT EXISTS subgenre_price ("
                "id SERIAL PRIMARY KEY, "
                "id_subgenre INTEGER REFERENCES subgenre(subgenre_id), "
                "id_quantity INTEGER REFERENCES quantity(quantity_id), "
                "price DECIMAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS payment_addresses ("
                "id SERIAL PRIMARY KEY, "
                "id_subgenre INTEGER REFERENCES subgenre(subgenre_id), "
                "id_quantity INTEGER REFERENCES quantity(quantity_id), "
                "address TEXT)")

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


async def add_subgenre_price(subgenre_id, quantity_id, price):
    cur.execute(
        "INSERT INTO subgenre_price (id_subgenre, id_quantity, price) VALUES (%s, %s, %s)",
        (subgenre_id, quantity_id, price)
    )
    conn.commit()


async def get_subgenre_price(subgenre_id, quantity_id):
    cur.execute(
        "SELECT price FROM subgenre_price WHERE id_subgenre = %s AND id_quantity = %s",
        (subgenre_id, quantity_id)
    )
    price = cur.fetchone()
    return price[0] if price else None


async def save_payment_address(subgenre_id, quantity_id, payment_address):
    cur.execute(
        "INSERT INTO payment_addresses (id_subgenre, id_quantity, address) VALUES (%s, %s, %s)",
        (subgenre_id, quantity_id, payment_address)
    )
    conn.commit()
