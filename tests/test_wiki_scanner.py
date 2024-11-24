import unittest
from unittest.mock import patch, MagicMock
import asyncio
from src.WikiScanner import WikiScanner
from src.WikiParser import WikiParser


class TestWikiScanner(unittest.IsolatedAsyncioTestCase):

    @patch('src.WikiScanner.WikiScanner._load_page_sync')
    @patch('asyncio.sleep', return_value=None)  # Мокируем asyncio.sleep, чтобы не было задержек
    async def test_load_page(self, mock_sleep, mock_load_page_sync):
        """Тестирование асинхронной загрузки страницы с retry"""

        # Мокируем успешную загрузку страницы
        mock_load_page_sync.return_value = '<html><body>Test</body></html>'

        # Создаём экземпляр сканера
        scanner = WikiScanner(db_path='test.db')

        # Вызываем асинхронную функцию
        result = await scanner._load_page('http://example.com')

        # Проверяем, что результат правильный
        self.assertEqual(result, '<html><body>Test</body></html>')

        # Проверяем, что _load_page_sync был вызван с нужным URL
        mock_load_page_sync.assert_called_once_with('http://example.com')

    @patch('src.WikiScanner.WikiScanner._load_page')
    @patch('src.WikiParser.WikiParser')
    async def test_check_redirect(self, MockParser, mock_load_page):
        """Тестирование проверки редиректов."""

        # Мокируем ответ от _load_page для страницы с редиректом
        mock_load_page.return_value = '''
            <div class="redirectMsg">
            <p>Перенаправление на:</p>
            <ul class="redirectText">
            <li>
            <a href="/wiki/Kazakhstan" title="Kazakhstan">Kazakhstan</a>
            </li></ul></div>
            '''

        # Мокируем парсер
        mock_parser = MagicMock()
        mock_parser.return_value = None
        MockParser.return_value = mock_parser

        # Создаём экземпляр сканера
        scanner = WikiScanner(db_path='test.db')

        # Вызываем асинхронную функцию
        result = await scanner.check_redirect('http://example.com')

        # Проверяем, что редирект был найден
        self.assertEqual(result, {'http://example.com': 'http://example.com/wiki/Kazakhstan'})

    @patch('src.WikiScanner.WikiScanner.fetch_links')
    @patch('src.WikiScanner.WikiScanner.check_redirect')
    async def test_start_scanning(self, mock_check_redirect, mock_fetch_links):
        """Тестирование начала сканирования."""

        # Мокируем возвращаемые данные для fetch_links
        mock_fetch_links.return_value = {'http://example.com/wiki/Test1', 'http://example.com/wiki/Test'}

        # Создаём экземпляр сканера
        scanner = WikiScanner(db_path='test.db')

        # Вызываем асинхронную функцию
        result = await scanner.start_scanning('http://example.com')

        # Проверяем, что результат правильный
        self.assertEqual(result, {'http://example.com': {'http://example.com/wiki/Test1', 'http://example.com/wiki/Test'}})
