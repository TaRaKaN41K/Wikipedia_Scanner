from urllib.parse import urljoin
from html.parser import HTMLParser


class WikiParser(HTMLParser):

    def __init__(self, start_url: str, links: set, redirect_links: set):
        super().__init__()
        self.start_url: str = start_url

        self.links: set = links
        self.redirect_links: set = redirect_links

        self.target_div_num: int = 0  # Номер целевого <div>
        self.div_count: int = 0  # Текущий уровень вложенности <div>

        self.in_target_div: bool = False  # Флаг для нахождения внутри целевого <div>
        self.in_redirect: bool = False  # Флаг для обработки перенаправлений

    def handle_starttag(self, tag: str, attrs: list) -> None:
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
