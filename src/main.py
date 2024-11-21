from WikiScanner import WikiScanner
from urllib.parse import unquote
from Database import Database


def main() -> None:
    """Основная функция CLI."""
    # parser = argparse.ArgumentParser(description="Обход статей Википедии.")
    # parser.add_argument("start_url", type=str, help="Ссылка на начальную статью Википедии.")
    # parser.add_argument("db_path", type=str, help="Путь к SQLite базе данных.")
    # parser.add_argument("--depth", type=int, default=6, help="Максимальная глубина обхода (по умолчанию: 6).")
    #
    # args = parser.parse_args()
    # crawl_wikipedia(args.start_url, args.db_path, args.depth)

    max_depth = 2

    start_url = 'https://ru.wikipedia.org/wiki/%D0%9C%D1%83%D0%B6_%D0%B8_%D0%B6%D0%B5%D0%BD%D0%B0'
    # start_url = 'https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%BE%D0%B5_(%D0%BE%D0%B7%D0%B5%D1%80%D0%BE,_%D0%92%D1%8F%D0%B7%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)'
    # start_url = 'https://ru.wikipedia.org/wiki/%D0%9A%D1%80%D0%BA%D0%BE%D0%B1%D0%B0%D0%B1%D0%B8%D1%87,_%D0%9C%D0%B8%D0%BB%D0%B0%D0%BD'

    print(f"Начинаем сканирование с {unquote(start_url)}")

    result_links = depth_scanning(start_url=start_url, max_depth=max_depth)

    print(f"Найдено {len(result_links)} уникальных ссылок:")
    for link in result_links:
        print(unquote(link))

    # db_links = db.fetch_all_links()
    # print(f"В базе данных {len(db_links)} уникальных ссылок:")
    # for db_link in db_links:
    #     print(db_link)


def depth_scanning(start_url: str, max_depth: int, current_depth: int = 1, visited_links: set[str] = None) -> set[str]:
    """
    Рекурсивное сканирование ссылок на Википедии.

    :param start_url: Начальная ссылка.
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

    print(f"Сканируем уровень {current_depth}, ссылка: {unquote(start_url)}")

    # Сканируем начальную ссылку
    try:
        new_links = scanner.start_scanning(start_url=start_url)
        visited_links.add(start_url)
        print(f'\nНайдено {len(new_links)} ссылок:')
        for link in new_links:
            print(unquote(link))
    except Exception as e:
        print(f"Ошибка при сканировании {unquote(start_url)}: {e}")
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
            depth_scanning(link, max_depth, current_depth + 1, visited_links)

    return visited_links


if __name__ == "__main__":
    scanner = WikiScanner()
    db = Database("Wikipedia_Links.db")
    db.create_links_table()
    main()
