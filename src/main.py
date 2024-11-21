from WikiScanner import WikiScanner, unquote
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

    scanner = WikiScanner()
    db = Database("Wikipedia_Links.db")
    db.create_users_table()

    start_url = 'https://ru.wikipedia.org/wiki/%D0%9C%D1%83%D0%B6_%D0%B8_%D0%B6%D0%B5%D0%BD%D0%B0'
    # start_url = 'https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%BE%D0%B5_(%D0%BE%D0%B7%D0%B5%D1%80%D0%BE,_%D0%92%D1%8F%D0%B7%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)'
    # start_url = 'https://ru.wikipedia.org/wiki/%D0%9A%D1%80%D0%BA%D0%BE%D0%B1%D0%B0%D0%B1%D0%B8%D1%87,_%D0%9C%D0%B8%D0%BB%D0%B0%D0%BD'

    print(f"Начинаем сканирование с {unquote(start_url)}")

    result_links = scanner.start_scanning(start_url=start_url)

    print(f"Найдено {len(result_links)} уникальных ссылок:")
    for link in result_links:
        print(unquote(link))
        db.insert_link(url=str(unquote(link)))

    db_links = db.fetch_all_links()
    print(f"В базе данных {len(db_links)} уникальных ссылок:")
    for db_link in db_links:
        print(db_link)


if __name__ == "__main__":
    main()
