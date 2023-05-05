# Парсер книг с сайта tululu.org
`parse_tululu.py` парсит книги с сайта [tululu.org](https://tululu.org/) по id. Скачивает книги и комментарии в формате .txt, обложку в исходном формате. Выводит в консоль название, автора и жанр.

`parse_tululu_category.py` парсит книги в жанре "Научная фантастика" с сайта [tululu.org](https://tululu.org/) по номеру страницы. Скачивает книги в формате .txt, обложку в исходном формате. Формирует json файл с названием книги, автором, жанром, комментариями и путями до обложки и txt.

## Окружение
### Зависимости
Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:

```bash
pip install -r requirements.txt
```

## Как запустить
Скрипты должны находиться в одной директории
### `parse_tululu.py`
Запуск на Linux(Python 3) или Windows:

```bash
$ python parse_tululu.py [-s START_ID] [-e END_ID]
```

Вы увидите:

```
Downloading...

1. Downloaded "Административные рынки СССР и России"
Author: Кордонский Симон
Genre: ('Деловая литература',)

2. No book with this ID

3. Downloaded "Азбука экономики"
Author: Строуп Р
Genre: ('Деловая литература',)

...

Done
```

### `parse_tululu_category.py`
Запуск на Linux(Python 3) или Windows:

```bash
$ python parse_tululu_category.py [-s START_PAGE] [-e END_PAGE] [-d DEST_FOLDER] [-j JSON_FOLDER] [--skip_imgs] [--skip_txt]
```

Вы увидите:

```
Downloading page number 1 ...

239. Downloaded "Алиби"

550. Downloaded "Бич небесный"

768. Downloaded "Цена посвящения Серый Ангел"

...

Done
```
Используйте `help`, чтобы узнать подробности
```bash
$ python parse_tululu_category.py --help
```
## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).