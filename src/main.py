import asyncio
import argparse
from urllib.parse import unquote

from WikiScanner import WikiScanner
from Database import Database


async def main() -> None:

    print(f"Начинаем сканирование с {unquote(start_url)}")

    start_urls: list[str] = [start_url]

    visited_links = await scanner.depth_scanning(urls=start_urls, max_depth=depth)

    print(f"\nВсего посещено {len(visited_links)} уникальных ссылок.")

    # redirect_links_len = await scanner.clear_redirect_links()
    #
    # print(f"\nНайдено {redirect_links_len} ссылок перенаправления.")

    return None


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

    scanner = WikiScanner(db_path=db_path)

    asyncio.run(main())
