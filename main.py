import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import argparse
import time


def parse_book_page(book_response):
    book_soup = BeautifulSoup(book_response.text, 'lxml')
    book_title = book_soup.select_one('.ow_px_td h1').text
    book_name, book_author = map(str.strip, book_title.split('::'))
    sanitized_book_name = sanitize_filename(book_name)
    cover_web_path = book_soup.select_one('.bookimage img')['src']
    cover_url = urljoin(book_response.url, cover_web_path)
    book_comments_soups = book_soup.select('.ow_px_td .black')
    book_comments = tuple(map(lambda x: x.text, book_comments_soups))
    book_genres_soups = book_soup.select('span.d_book a')
    book_genres = tuple(map(lambda x: x.text, book_genres_soups))

    return {
        'name': sanitized_book_name,
        'author': book_author,
        'cover_url': cover_url,
        'comments': book_comments,
        'genres': book_genres,
    }


def check_for_redirect(response, error_msg):
    if response.is_redirect:
        raise requests.HTTPError(error_msg)


def download_image(image_url, image_path):
    *_, image_name = urlparse(image_url).path.split('/')
    image_full_path = image_path / image_name
    if image_full_path.is_file():
        return image_full_path
    image_response = requests.get(image_url, allow_redirects=False)
    image_response.raise_for_status()
    check_for_redirect(image_response, f'Can\'t download "{image_name}"')
    with open(image_full_path, 'wb') as file:
        file.write(image_response.content)
    return image_full_path


def download_txt(txt_url, txt_id, txt_name, txt_path):
    txt_full_path = txt_path / f'{txt_id}. {txt_name}.txt'
    if txt_full_path.is_file():
        return txt_full_path
    params = {'id': txt_id}
    txt_response = requests.get(txt_url, params=params, allow_redirects=False)
    txt_response.raise_for_status()
    check_for_redirect(txt_response, f'{txt_id}. Can\'t download "{txt_name}"')
    with open(txt_full_path, 'wb') as file:
        file.write(txt_response.content)
    return txt_full_path


def download_comments(book_comments, book_id, comments_path):
    comments_full_path = comments_path / f'{book_id}.txt'
    if not book_comments or comments_full_path.is_file():
        return
    with open(comments_path / f'{book_id}.txt', 'wt', encoding='utf-8') as file:
        for comment in book_comments:
            file.write(f'{comment}\n')


def main():
    parser = argparse.ArgumentParser(description='Download books from tululu.org using books ids')
    parser.add_argument( '-s', '--start_id', help='first book id (default: 1)', type=int, default=1)
    parser.add_argument( '-e', '--end_id', help='last book id (default: 1)', type=int, default=1)
    args = parser.parse_args()
    if args.start_id > args.end_id:
        exit('Wrong input')

    print('Downloading...\n')
    books_path = Path('books')
    books_path.mkdir(exist_ok=True)
    covers_path = Path('images')
    covers_path.mkdir(exist_ok=True)
    comments_path = Path('comments')
    comments_path.mkdir(exist_ok=True)

    for book_id in range(args.start_id, args.end_id + 1):
        while True:
            try:
                page_url = f'https://tululu.org/b{book_id}/'
                book_response = requests.get(page_url, allow_redirects=False)
                book_response.raise_for_status()
                check_for_redirect(book_response, f'{book_id}. No book with this ID')
                book = parse_book_page(book_response)
                txt_url = 'https://tululu.org/txt.php'
                download_txt(txt_url, book_id, book['name'], books_path)
                print(f'{book_id}. Downloaded "{book["name"]}"')
                print(f'Author: {book["author"]}')
                print(f'Genre: {book["genres"]}')
                download_comments(book['comments'], book_id, comments_path)
                download_image(book['cover_url'], covers_path)
                break
            except requests.ConnectionError:
                print('Connection problem. Reconnecting...')
                time.sleep(5)
            except requests.HTTPError as e:
                print(e)
                break
        print()
    print('Done')


if __name__ == '__main__':
    main()
