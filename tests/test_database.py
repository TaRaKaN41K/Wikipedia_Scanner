import unittest
from src.Database import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Этот метод выполняется перед каждым тестом. Создаём базу данных для тестов."""
        self.db = Database('test_Wikipedia_Links.db')  # Используем реальную базу данных для тестов
        self.db.create_links_table()  # Создаём таблицу перед каждым тестом

    def tearDown(self):
        """Этот метод выполняется после каждого теста. Здесь можно очистить базу данных, если необходимо."""
        self.db.connect()
        self.db.cursor.execute("DELETE FROM WikiLinks")  # Очищаем таблицу
        self.db.connection.commit()  # Сохраняем изменения
        self.db.close()  # Закрываем соединение с базой данных после каждого теста

    def test_create_links_table(self):
        """Проверка, что таблица создана без ошибок."""
        self.db.connect()
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='WikiLinks';")
        table = self.db.cursor.fetchone()
        self.db.close()
        self.assertIsNotNone(table)  # Проверка, что таблица существует

    def test_insert_link(self):
        """Тестирование вставки ссылки в таблицу."""
        url = "https://example.com"
        self.db.insert_link(url)

        # Проверяем, что ссылка была добавлена
        links = self.db.fetch_all_links()
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0][1], url)

    def test_insert_duplicate_link(self):
        """Проверка, что дублирующаяся ссылка не вставляется."""
        url = "https://example.com"
        self.db.insert_link(url)
        self.db.insert_link(url)  # Пытаемся вставить её ещё раз

        # Проверяем, что в базе только одна ссылка
        links = self.db.fetch_all_links()
        self.assertEqual(len(links), 1)

    def test_fetch_all_links(self):
        """Проверка выборки всех ссылок."""
        url1 = "https://example.com"
        url2 = "https://another.com"
        self.db.insert_link(url1)
        self.db.insert_link(url2)

        links = self.db.fetch_all_links()
        self.assertEqual(len(links), 2)
        self.assertIn((1, url1), links)
        self.assertIn((2, url2), links)

    def test_insert_invalid_link(self):
        """Тестирование на вставку некорректных данных."""
        with self.assertRaises(Exception):
            self.db.insert_link(None)  # Попытка вставить None как URL

    def test_fetch_empty_table(self):
        """Проверка извлечения данных из пустой таблицы."""
        links = self.db.fetch_all_links()
        self.assertEqual(len(links), 0)  # Таблица должна быть пуста

    def test_integrity_error_on_duplicate_link(self):
        """Проверка того, что вставка дублирующегося URL не вызывает ошибок и выводит сообщение."""
        url = "https://example.com"
        self.db.insert_link(url)
        self.db.insert_link(url)  # Вставка дублирующейся ссылки
        links = self.db.fetch_all_links()
        self.assertEqual(len(links), 1)  # Должно быть только одно вхождение этой ссылки