import asyncio
import urllib.request
from urllib.parse import unquote
from urllib.error import HTTPError

from WikiParser import WikiParser


class WikiScanner:

    @staticmethod
    def _load_page_sync(url: str) -> str:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")

    async def _load_page(self, url: str, retries: int = 10) -> str:
        loop = asyncio.get_running_loop()

        for attempt in range(retries):
            try:
                return await loop.run_in_executor(None, self._load_page_sync, url)
            except HTTPError as e:
                if e.code == 429:  # Сервер перегружен
                    if attempt < retries - 1:
                        await asyncio.sleep(2)  # Ждем перед повторной попыткой
                    else:
                        raise Exception(f"Превышено количество попыток для {url}: {e}")
                else:
                    raise Exception(f"Ошибка {url}: {e}.")
            except urllib.error.URLError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)  # Ждем перед повторной попыткой
                else:
                    raise Exception(f"Сетевая ошибка {url}: {e}")
            except ConnectionResetError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)  # Пауза перед повторной попыткой
                else:
                    raise Exception(f"Ошибка подключения {url}: {e}")
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)  # Общая пауза для любых других ошибок
                else:
                    raise Exception(f"Не удалось загрузить {url}: {e}")

    async def fetch_links(self, url: str) -> set[str]:
        links: set[str] = set()
        redirect_links: set[str] = set()

        parser = WikiParser(start_url=url, links=links, redirect_links=redirect_links)

        try:
            content = await self._load_page(url)
            parser.feed(content)

            # tasks = []
            #
            # # Создаём задачи для проверки всех ссылок
            # for link in links:
            #     tasks.append(self.check_redirect(link))
            #
            # results: list[dict[str, str | None]] = list(await asyncio.gather(*tasks))
            #
            # # Распаковываем и объединяем словари
            # for result in results:
            #     if list(result.values())[0] is not None:
            #         links.remove(list(result.keys())[0])
            #         links.add(list(result.values())[0])

            return links

        except Exception as e:
            raise Exception(f"Ошибка загрузки страницы {url}: {e}")

    async def check_redirect(self, link: str) -> dict[str, str | None]:

        links: set[str] = set()
        redirect_links: set[str] = set()

        parser = WikiParser(start_url=link, links=links, redirect_links=redirect_links)

        try:
            request_url = f"{link}?redirect=no"
            content = await self._load_page(request_url)
            parser.feed(content)

            redirect_link = next(iter(redirect_links), None)

            return {link: redirect_link}

        except Exception as e:
            raise Exception(f"Ошибка проверки перенаправления для {link}: {e}")

    async def start_scanning(self, start_url: str) -> dict[str, set[str]]:

        try:

            result_links = await self.fetch_links(start_url)

        except Exception as e:
            raise Exception(f"Ошибка при сканировании {unquote(start_url)}: {e}")

        return {start_url: result_links}
