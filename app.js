const express = require('express');
const { Pool } = require('pg')  // Импортируем Pool из библиотеки pg
const path = require('path');
const cors = require('cors'); // Добавляем поддержку CORS

const app = express();
const PORT = process.env.PORT || 3000; // Используйте переменную окружения PORT для порта

// Настройте подключение к базе данных PostgreSQL
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,  // Используйте переменную окружения для строки подключения
    ssl: {
        rejectUnauthorized: false,  // Необходимо для подключения к базе данных на Heroku
    },
});


app.use(cors()); // Разрешаем CORS для всех запросов


app.get('/city', (req, res) => {
    pool.query('SELECT city_id, name FROM city', (err, result) => {
        if (err) {
            res.status(500).json({error: 'Database error'});
            return;
        }
        res.json(result.rows);
    });
});


app.get('/city/:cityId/genres', async (req, res) => {
    const cityId = req.params.cityId;

    if (!Number.isInteger(Number(cityId))) {
        res.status(400).json({ error: 'City ID is missing' });
        return;
    }

    try {
        const query = 'SELECT DISTINCT g.name FROM genre g JOIN items i ON g.genre_id = i.id_genre WHERE i.id_city = $1';
        const result = await pool.query(query, [cityId]);
        res.json(result.rows);
    } catch (error) {
        console.error('Database error:', error);
        res.status(500).json({ error: 'Database error' });
    }
});


app.get('/city/:cityId/genre/:genreId/subgenres', async (req, res) => {
    const cityId = req.params.cityId;
    const genreId = req.params.genreId;

    if (!Number.isInteger(Number(cityId)) || !Number.isInteger(Number(genreId))) {
        res.status(400).json({ error: 'City ID or Genre ID is missing'});
        return;
    }

    try {
        const query = 'SELECT sg.name FROM subgenre sg JOIN items i ON sg.subgenre_id = i.id_subgenre WHERE i.id_city = $1 AND i.id_genre = $2';
        const result = await pool.query(query, [cityId, genreId]);
        res.json(result.rows);
    } catch (error) {
        console.error('Database error:', error);
        res.status(500).json({ error: 'Database error'});
    }
});

// Обработчик GET-запроса для главной страницы
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});


app.post('/send-data', express.json(), (req, res) => {
    const receivedData = req.body;

    res.json({message: 'Данные успешно обработаны'})
})


app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
