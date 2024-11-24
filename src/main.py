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

    print(f"\nСканируем уровень {current_depth}")

    if visited_links is None:
        visited_links = set()

    # Сканируем начальную ссылку
    try:
        tasks = []

        # Создаём задачи для проверки всех ссылок
        for url in urls:
            tasks.append(scanner.start_scanning(start_url=url))

        results: list[dict[str, set[str]]] = list(await asyncio.gather(*tasks))

        links_level_count: int = 0

        for result in results:
            visited_links.add(list(result.keys())[0])
            links_level_count += len(list(result.values())[0])

        print(f'Найдено {links_level_count} ссылок на уровне {current_depth}')

        all_links_from_level = {str(unquote(link)) for result in results for links in result.values() for link in links}

        print(f'Из них {len(all_links_from_level)} ссылок уникальных на уровне {current_depth}')

        all_links_for_next_level = {str(link) for result in results for links in result.values() for link in links}
        new_links_for_next_level = all_links_for_next_level - visited_links

        db_links_tuple: list[tuple[int, str]] = db.fetch_all_links()
        db_links: set[str] = {link for _, link in db_links_tuple}

        result_set = all_links_from_level | db_links

        print("Вставляем ссылки")

        # Сохраняем новые ссылки в базу данных
        for link in result_set:
            db.insert_link(url=link)

        print("Добавлены все ссылки на уровне {}".format(current_depth))

        if current_depth < max_depth:
            # Рекурсивно сканируем каждую новую ссылку если она не посещена ещё
            await depth_scanning(
                urls=list(new_links_for_next_level),
                max_depth=max_depth,
                current_depth=current_depth + 1,
                visited_links=visited_links
            )

        return visited_links

    except Exception as e:
        print(f"Ошибка при сканировании: {e}")
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
