import urllib.request
from urllib.parse import urljoin
from html.parser import HTMLParser
import time

import asyncio


class WikiScanner(HTMLParser):
    """
    Класс для парсинга страниц Википедии, извлечения ссылок и проверки перенаправлений.
    """

    def __init__(self):
        """
        Инициализация экземпляра WikiScanner.

        :param max_depth: Максимальная глубина сканирования (по умолчанию 6).
        """
        super().__init__()
        self.start_url: str = ''
        self.links: set = set()  # Ссылки на статьи Википедии
        self.redirect_links: set = set()  # Перенаправленные ссылки
        self.target_div_num: int = 0  # Номер целевого <div>
        self.div_count: int = 0  # Текущий уровень вложенности <div>
        self.in_target_div: bool = False  # Флаг для нахождения внутри целевого <div>
        self.in_redirect: bool = False  # Флаг для обработки перенаправлений

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """
        Обработка начальных тегов HTML.

        :param tag: Тег HTML.
        :param attrs: Список атрибутов тега.
        """
        if tag == "div":
            self.div_count += 1
            for attr, value in attrs:
                if attr == "class" and value == "mw-content-ltr mw-parser-output":
                    self.in_target_div = True
                    self.target_div_num = self.div_count
                if attr == "class" and value == "redirectMsg":
                    self.in_redirect = True

        if tag == "a":
            for attr, value in attrs:
                if (self.in_target_div and
                        attr == "href" and
                        value.startswith("/wiki/") and
                        not any(c in value for c in [":", "#"]) and
                        not self.in_redirect):

                    absolute_url = urljoin(self.start_url, value)
                    self.links.add(absolute_url)

                if (self.in_redirect and
                        attr == "href" and
                        value.startswith("/wiki/") and
                        not any(c in value for c in [":", "#"])):

                    absolute_redirect_url = urljoin(self.start_url, value)
                    self.redirect_links.add(absolute_redirect_url)

    def handle_endtag(self, tag: str) -> None:
        """
        Обработка закрывающих тегов HTML.

        :param tag: Закрывающий тег HTML.
        """
        if tag == "div":
            if self.div_count > 0:
                self.div_count -= 1
            else:
                raise ValueError("Неожиданный конец тега div")
        if tag == "div" and self.div_count == self.target_div_num - 1 and self.in_target_div:
            self.in_target_div = False
            self.target_div_num = 0
        if tag == "a" and self.in_redirect:
            self.in_redirect = False

    def reset_parser(self) -> None:
        """
        Сброс состояния парсера перед обработкой новой страницы.
        """
        self.links.clear()
        self.redirect_links.clear()
        self.in_target_div = False
        self.in_redirect = False
        self.target_div_num = 0
        self.div_count = 0

    @staticmethod
    def _load_page(url: str) -> str:
        """
        Загрузка страницы (синхронная).
        """
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")

    async def fetch_links(self, url: str) -> None:
        """
        Загрузка веб-страницы и извлечение ссылок.

        :param url: URL-адрес страницы для обработки.
        :raises Exception: В случае ошибки загрузки или парсинга страницы.
        """
        self.reset_parser()
        loop = asyncio.get_running_loop()
        try:
            content = await loop.run_in_executor(None, self._load_page, url)
            # response = urllib.request.urlopen(url)
            # content = response.read().decode("utf-8")
            self.feed(content)
        except Exception as e:
            raise Exception(f"Ошибка загрузки страницы {url}: {e}")

    async def check_redirect(self, link: str) -> None:
        """
        Проверка, является ли ссылка перенаправлением.

        :param link: URL для проверки.
        :raises Exception: В случае ошибки проверки перенаправления.
        """
        self.reset_parser()
        loop = asyncio.get_running_loop()
        try:
            # request_url = f"{link}?redirect=no"
            # response = urllib.request.urlopen(request_url)
            # content = response.read().decode("utf-8")
            content = await loop.run_in_executor(None, self._load_page, f"{link}?redirect=no")
            self.feed(content)
        except Exception as e:
            raise Exception(f"Ошибка проверки перенаправления для {link}: {e}")

    async def start_scanning(self, start_url: str) -> set[str]:
        """
        Запуск сканирования с указанного URL.

        :param start_url: Начальный URL для сканирования.
        :return: Множество уникальных ссылок (включая целевые URL перенаправлений).
        """
        self.start_url = start_url
        await self.fetch_links(start_url)

        result_links = set(self.links)
        links = set(self.links)

        for link in links:
            await self.check_redirect(link)
            if len(self.redirect_links) == 1:
                result_links.remove(link)
                result_links |= set(self.redirect_links)
            time.sleep(1)

        return result_links

# import asyncio
# from urllib.request import urlopen
# from html.parser import HTMLParser
#
#
# class AsyncLinkScanner(HTMLParser):
#     def __init__(self):
#         super().__init__()
#         self.links = set()
#         self.redirect_links = set()
#         self.start_url = ""
#
#     def reset_parser(self):
#         self.links.clear()
#         self.redirect_links.clear()
#
#     def handle_starttag(self, tag, attrs):
#         if tag == "a":
#             for attr_name, attr_value in attrs:
#                 if attr_name == "href":
#                     self.links.add(attr_value)
#
#     async def fetch_links(self, url: str) -> None:
#         """
#         Асинхронная загрузка веб-страницы и извлечение ссылок.
#         """
#         self.reset_parser()
#         loop = asyncio.get_running_loop()
#         try:
#             # Выполнение загрузки страницы в отдельном потоке
#             content = await loop.run_in_executor(None, self._load_page, url)
#             self.feed(content)
#         except Exception as e:
#             raise Exception(f"Ошибка загрузки страницы {url}: {e}")
#
#     async def check_redirect(self, link: str) -> None:
#         """
#         Асинхронная проверка, является ли ссылка перенаправлением.
#         """
#         self.reset_parser()
#         loop = asyncio.get_running_loop()
#         try:
#             # Выполнение проверки перенаправления в отдельном потоке
#             content = await loop.run_in_executor(None, self._load_page, f"{link}?redirect=no")
#             self.feed(content)
#         except Exception as e:
#             raise Exception(f"Ошибка проверки перенаправления для {link}: {e}")
#
#     def _load_page(self, url: str) -> str:
#         """
#         Загрузка страницы (синхронная).
#         """
#         with urlopen(url) as response:
#             return response.read().decode("utf-8")
#
#     async def start_scanning(self, start_url: str) -> set[str]:
#         """
#         Асинхронный запуск сканирования с указанного URL.
#         """
#         self.start_url = start_url
#         await self.fetch_links(start_url)
#
#         result_links = set(self.links)
#         links = set(self.links)
#
#         for link in links:
#             await self.check_redirect(link)
#             if len(self.redirect_links) == 1:
#                 result_links.remove(link)
#                 result_links |= set(self.redirect_links)
#             await asyncio.sleep(1)  # Асинхронная задержка
#
#         return result_links
