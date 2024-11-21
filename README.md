# Сканер Википедии

CLI утилита, которая:
1) Получает на вход ссылку на статью в википедии.
2) Парсит полученную на вход страницу и ищет на ней ссылки на другие статьи в википедии
3) Собирает их и записывает в базу SQLite.
4) Открывает полученные ссылки, ищет на них новые ссылки на другие статьи
5) Записывает в базу
6) Пункты `4` и `5` повторяются, пока глубина поиска не достигнет 6.
7) Все сохранённые ссылки в базе - уникальные

Примечание:
- Язык выполнения `python3.12`
- Используются только инструменты стандартной библиотеки 
- Код типизирован (используется аннотации типов)
- Код декомпозирован 
- Данный код покрыт тестами
