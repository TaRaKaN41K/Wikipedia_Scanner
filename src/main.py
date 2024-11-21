import asyncio
import argparse
from urllib.parse import unquote

from WikiScanner import WikiScanner
from Database import Database


async def main() -> None:

    print(f"Начинаем сканирование с {unquote(start_url)}")

    result_links = await depth_scanning(url=start_url, max_depth=depth)

    print(f"Найдено {len(result_links)} уникальных ссылок:")
    for link in result_links:
        print(unquote(link))


async def depth_scanning(url: str, max_depth: int, current_depth: int = 1, visited_links: set[str] = None) -> set[str]:
    """
    Рекурсивное сканирование ссылок на Википедии.

    :param url: Начальная ссылка.
    :param max_depth: Максимальная глубина обхода.
    :param current_depth: Текущая глубина (по умолчанию 1).
    :param visited_links: Набор уже посещенных ссылок (по умолчанию None).
    :return: Набор уникальных ссылок, найденных в процессе сканирования.
    """
    if visited_links is None:
        visited_links = set()

    # Останавливаем рекурсию, если достигнута максимальная глубина
    if current_depth > max_depth:
        return visited_links

    print(f"Сканируем уровень {current_depth}, ссылка: {unquote(url)}")

    # Сканируем начальную ссылку
    try:
        new_links = await scanner.start_scanning(start_url=url)
        visited_links.add(url)
        print(f'\nНайдено {len(new_links)} ссылок:')
        for link in new_links:
            print(unquote(link))
    except Exception as e:
        print(f"Ошибка при сканировании {unquote(url)}: {e}")
        return visited_links

    db_links_tuple: list[tuple[int, str]] = db.fetch_all_links()
    db_links: list[str] = [link for _, link in db_links_tuple]

    # Сохраняем новые ссылки в базу данных и обновляем список посещённых ссылок
    for link in new_links:
        if unquote(link) not in db_links:
            db.insert_link(url=str(unquote(link)))

    # Рекурсивно сканируем каждую новую ссылку
    for link in new_links:
        if link not in visited_links:
            await depth_scanning(link, max_depth, current_depth + 1, visited_links)

    return visited_links


if __name__ == "__main__":

    """Основная функция CLI."""
    parser = argparse.ArgumentParser(description="Обход статей Википедии.")

    parser.add_argument(
        "start_url",
        type=str,
        help="Ссылка на начальную статью Википедии."
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="Wikipedia_Links.db",
        help="Путь к базе данных (по умолчанию: Wikipedia_Links.db)."
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=6,
        help="Максимальная глубина обхода (по умолчанию: 6)."
    )

    args = parser.parse_args()

    depth = args.depth
    start_url = args.start_url
    db_path = args.db_path

    scanner = WikiScanner()
    db = Database(db_path)
    db.create_links_table()

    # start_url = 'https://ru.wikipedia.org/wiki/%D0%9C%D1%83%D0%B6_%D0%B8_%D0%B6%D0%B5%D0%BD%D0%B0'
    # start_url = 'https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%BE%D0%B5_(%D0%BE%D0%B7%D0%B5%D1%80%D0%BE,_%D0%92%D1%8F%D0%B7%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)'
    # start_url = 'https://ru.wikipedia.org/wiki/%D0%9A%D1%80%D0%BA%D0%BE%D0%B1%D0%B0%D0%B1%D0%B8%D1%87,_%D0%9C%D0%B8%D0%BB%D0%B0%D0%BD'

    asyncio.run(main())
