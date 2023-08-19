const express = require('express');
const sqlite3 = require('sqlite3');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000; // Используйте переменную окружения PORT для порта

const db = new sqlite3.Database(path.join(__dirname, 'tg.db')); // Используйте абсолютный путь к базе данных

app.get('/city', (req, res) => {
    db.all('SELECT name FROM city', (err, rows) => {
        if (err) {
            res.status(500).json({ error: 'Database error' });
            return;
        }
        res.json(rows);
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
