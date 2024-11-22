import asyncio
import argparse
from urllib.parse import unquote

from WikiScanner import WikiScanner
from Database import Database


async def main() -> None:

    print(f"Начинаем сканирование с {unquote(start_url)}")

    start_urls: list[str] = [start_url]

    visited_links = await depth_scanning(urls=start_urls, max_depth=depth)

    print(f"\nВсего посещено {len(visited_links)} уникальных ссылок.")

    return None


async def depth_scanning(urls: list[str], max_depth: int, current_depth: int = 1, visited_links: set[str] = None) -> set[str]:

    if visited_links is None:
        visited_links = set()

    # Останавливаем рекурсию, если достигнута максимальная глубина
    if current_depth > max_depth:
        return visited_links

    # Сканируем начальную ссылку
    try:
        tasks = []

        # Создаём задачи для проверки всех ссылок
        for url in urls:
            if url not in visited_links:
                tasks.append(scanner.start_scanning(start_url=url, current_depth=current_depth))
                await asyncio.sleep(0.1)  # Задержка между задачами

        results: list[dict[str, set[str]]] = list(await asyncio.gather(*tasks))

        for result in results:
            visited_links.add(list(result.keys())[0])
            print(f'\nНайдено {len(list(result.values())[0])} ссылок на уровне {current_depth}')
            # for link in list(result.values())[0]:
            #     print(unquote(link))

    except Exception as e:
        print(f"Ошибка при сканировании: {e}")
        return visited_links

    db_links_tuple: list[tuple[int, str]] = db.fetch_all_links()
    db_links: list[str] = [link for _, link in db_links_tuple]

    # Сохраняем новые ссылки в базу данных
    for result in results:
        for link in list(result.values())[0]:
            if unquote(link) not in db_links:
                db.insert_link(url=str(unquote(link)))

        # Рекурсивно сканируем каждую новую ссылку
        await depth_scanning(
            urls=list(list(result.values())[0]),
            max_depth=max_depth,
            current_depth=current_depth + 1,
            visited_links=visited_links
        )

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

    asyncio.run(main())
