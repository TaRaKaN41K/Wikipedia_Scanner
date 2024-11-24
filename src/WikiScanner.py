import asyncio
import urllib.request
from urllib.parse import unquote
from urllib.error import HTTPError

from WikiParser import WikiParser
from Database import Database


class WikiScanner:

    def __init__(self, db_path):
        self.db = Database(db_path)
        self.db.create_links_table()

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

    async def depth_scanning(self, urls: list[str], max_depth: int, current_depth: int = 1, visited_links: set[str] = None) -> \
    set[str]:

        print(f"\nСканируем уровень {current_depth}")

        if visited_links is None:
            visited_links = set()

        # Сканируем начальную ссылку
        try:
            tasks = []

            # Создаём задачи для проверки всех ссылок
            for url in urls:
                tasks.append(self.start_scanning(start_url=url))

            results: list[dict[str, set[str]]] = list(await asyncio.gather(*tasks))

            links_level_count: int = 0

            for result in results:
                visited_links.add(list(result.keys())[0])
                links_level_count += len(list(result.values())[0])

            print(f'Найдено {links_level_count} ссылок на уровне {current_depth}')

            all_links_from_level = {link for result in results for links in result.values() for link in
                                    links}

            print(f'Из них {len(all_links_from_level)} ссылок уникальных на уровне {current_depth}')

            all_links_for_next_level = {str(link) for result in results for links in result.values() for link in links}
            new_links_for_next_level = all_links_for_next_level - visited_links

            db_links_tuple: list[tuple[int, str]] = self.db.fetch_all_links()
            db_links: set[str] = {link for _, link in db_links_tuple}

            result_set = all_links_from_level | db_links

            print("Вставляем ссылки")

            # Сохраняем новые ссылки в базу данных
            for link in result_set:
                self.db.insert_link(url=link)

            print("Добавлены все ссылки на уровне {}".format(current_depth))

            if current_depth < max_depth:
                # Рекурсивно сканируем каждую новую ссылку если она не посещена ещё
                await self.depth_scanning(
                    urls=list(new_links_for_next_level),
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    visited_links=visited_links
                )

            return visited_links

        except Exception as e:
            print(f"Ошибка при сканировании: {e}")
            return visited_links

    async def clear_redirect_links(self) -> int:
        try:

            db_links_tuple: list[tuple[int, str]] = self.db.fetch_all_links()
            db_links: set[str] = {link for _, link in db_links_tuple}

            tasks = []

            # Создаём задачи для проверки всех ссылок
            for link in db_links:
                tasks.append(self.check_redirect(link))

            results: list[dict[str, str | None]] = list(await asyncio.gather(*tasks))
            redirect_count: int = 0

            # Распаковываем и объединяем словари
            for result in results:
                if list(result.values())[0] is not None:
                    redirect_count += 1
                    self.db.delete_link(url=list(result.keys())[0])
                    self.db.insert_link(url=list(result.values())[0])

            return redirect_count

        except Exception as e:
            raise Exception(f"Ошибка при чистке перенаправлений: {e}")
