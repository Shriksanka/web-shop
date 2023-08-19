const express = require('express');
const sqlite3 = require('sqlite3');
const path = require('path');
const cors = require('cors'); // Добавляем поддержку CORS

const app = express();
const PORT = process.env.PORT || 3000; // Используйте переменную окружения PORT для порта

const db = new sqlite3.Database(path.join(__dirname, 'tg.db')); // Используйте абсолютный путь к базе данных


app.use(cors()); // Разрешаем CORS для всех запросов


app.get('/city', (req, res) => {
    db.all('SELECT name FROM city', (err, rows) => {
        if (err) {
            res.status(500).json({ error: 'Database error' });
            return;
        }
        res.json(rows);
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
