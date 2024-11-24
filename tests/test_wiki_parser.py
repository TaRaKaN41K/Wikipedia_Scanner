import unittest
from pathlib import Path
from src.WikiParser import WikiParser


class TestWikiParser(unittest.TestCase):

    def setUp(self):
        """Инициализация перед каждым тестом."""
        self.start_url = "https://en.wikipedia.org"
        self.links = set()
        self.redirect_links = set()
        self.parser = WikiParser(start_url=self.start_url, links=self.links, redirect_links=self.redirect_links)
        self.test_dir = Path("tests/html_patterns")

    def load_html(self, file_name: str) -> str:
        """Загружает HTML-содержимое из файла."""
        with open(self.test_dir / file_name, "r", encoding="utf-8") as file:
            return file.read()

    def test_parse_valid_links(self):
        html_content = self.load_html("valid_links.html")
        self.parser.feed(html_content)
        expected_links = {
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
        }
        self.assertEqual(self.links, expected_links)

    def test_ignore_invalid_links(self):
        html_content = self.load_html("invalid_links.html")
        self.parser.feed(html_content)
        self.assertEqual(self.links, set())  # Ссылки с `:` и `#` должны быть проигнорированы

    def test_redirect_links(self):
        html_content = self.load_html("redirect_links.html")
        self.parser.feed(html_content)
        expected_redirects = {"https://en.wikipedia.org/wiki/New_Page"}
        self.assertEqual(self.redirect_links, expected_redirects)

    def test_nested_div_handling(self):
        html_content = self.load_html("nested_div.html")
        self.parser.feed(html_content)
        expected_links = {"https://en.wikipedia.org/wiki/Deep_Learning"}
        self.assertEqual(self.links, expected_links)

    def test_invalid_div_closing(self):
        html_content = self.load_html("invalid_closing.html")
        with self.assertRaises(ValueError) as context:
            self.parser.feed(html_content)
        self.assertIn("Неожиданный конец тега div", str(context.exception))

    def test_empty_content(self):
        html_content = self.load_html("empty.html")
        self.parser.feed(html_content)
        self.assertEqual(self.links, set())
        self.assertEqual(self.redirect_links, set())

    def test_combined_links(self):
        html_content = self.load_html("combined.html")
        self.parser.feed(html_content)
        expected_links = {"https://en.wikipedia.org/wiki/Python"}
        expected_redirects = {"https://en.wikipedia.org/wiki/New_Page"}
        self.assertEqual(self.links, expected_links)
        self.assertEqual(self.redirect_links, expected_redirects)