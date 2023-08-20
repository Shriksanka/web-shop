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

const {
    get_available_genres_by_city
} = require('app/database.py');

app.use(cors()); // Разрешаем CORS для всех запросов


app.get('/city', (req, res) => {
    pool.query('SELECT name FROM city', (err, result) => {
        if (err) {
            res.status(500).json({error: 'Database error'});
            return;
        }
        res.json(result.rows);
    });
});


app.get('/city/:cityId/genres', async (req, res) => {
    const cityId = req.params.cityId;

    try {
        const genres = await get_available_genres_by_city(cityId);
        res.json(genres);
    } catch (error) {
        res.status(500).json({error: 'Database error'});
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
