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

    def create_links_table(self):
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
        """ Вставляет ссылку в таблицу WikiLinks. """

        if not url:
            raise ValueError("URL не может быть None или пустым!")

        try:
            self.connect()

            # Проверяем, существует ли ссылка уже в базе
            self.cursor.execute("SELECT 1 FROM WikiLinks WHERE url = ?", (url,))
            if self.cursor.fetchone():
                # print(f"Ссылка {url} уже существует в базе данных.")
                return  # Возвращаемся, если ссылка уже существует

            # Вставляем новую ссылку
            self.cursor.execute('''
                INSERT INTO WikiLinks (url)
                VALUES (?)
            ''', (url,))
            self.connection.commit()

        except Exception as e:
            print(f"Ошибка при вставке ссылки: {e}")
        finally:
            self.close()

    def delete_link(self, url: str):
        """
        Удаляет ссылку из таблицы WikiLinks.

        :param url: Ссылка, которую нужно удалить.
        """
        if not url:
            raise ValueError("URL не может быть None или пустым!")

        try:
            self.connect()

            # Проверяем, существует ли ссылка в базе
            self.cursor.execute("SELECT 1 FROM WikiLinks WHERE url = ?", (url,))
            if not self.cursor.fetchone():
                print(f"Ссылка {url} не найдена в базе данных.")
                return  # Возвращаемся, если ссылка не найдена

            # Удаляем ссылку
            self.cursor.execute("DELETE FROM WikiLinks WHERE url = ?", (url,))
            self.connection.commit()
            print(f"Ссылка {url} успешно удалена из базы данных.")

        except Exception as e:
            print(f"Ошибка при удалении ссылки: {e}")
        finally:
            self.close()

    def fetch_all_links(self) -> list[tuple[int, str]]:
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
