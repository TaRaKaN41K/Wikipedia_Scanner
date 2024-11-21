import sqlite3


class Database:
    """
    Класс для управления базой данных SQLite.
    """

    def __init__(self, db_name: str):
        """
        Инициализирует подключение к базе данных.

        :param db_name: Имя файла базы данных.
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Устанавливает соединение с базой данных.
        """
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_users_table(self):
        """
        Создает таблицу WikiLinks, если она не существует.
        """
        self.connect()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS WikiLinks (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL
        )
        ''')
        self.connection.commit()
        self.close()

    def insert_link(self, url: str):
        """
        Вставляет ссылку на статью в Википедии в таблицу WikiLinks.

        :param url: Ссылка на статью в Википедии.
        """
        try:
            self.connect()
            self.cursor.execute('''
            INSERT INTO WikiLinks (url)
            VALUES (?)
            ''', (url,))  # Передача url как кортеж
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"Ссылка {url} уже существует в базе данных.")
        except Exception as e:
            print(f"Ошибка при вставке ссылки: {e}")

    def fetch_all_links(self):
        """
        Возвращает все ссылки на статьи из таблицы WikiLinks.

        :return: Список кортежей со ссылками на статьи.
        """
        self.connect()
        self.cursor.execute('SELECT * FROM WikiLinks')
        users = self.cursor.fetchall()
        self.close()
        return users

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
