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

    pool.query('SELECT DISTINCT g.name FROM genre g JOIN subgenre sg ON g.genre_id = sg.id_genre JOIN items i ON sg.subgenre_id = i.id_subgenre WHERE i.id_city = $1', [cityId], (err, result) => {
        if (err) {
            console.error('Database error: ', err);
            res.status(500).json({ error: 'Database error' });
            return;
        }
        console.log('Query result:', result.rows);
        res.json(result.rows);
    });
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
