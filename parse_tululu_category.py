import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from parse_tululu import *
import json
import argparse
import time


def main():
    parser = argparse.ArgumentParser(
        description='Download "Научная фантастика" books from tululu.org using page numbers')
    parser.add_argument(
        '-s', '--start_page', help='first page number (default: 1)', type=int, default=1)
    parser.add_argument(
        '-e', '--end_page', help='last page number (default: 1)', type=int, default=1)
    parser.add_argument(
        '-d', '--dest_folder', help='folder to save data (default: current dir)', default='')
    parser.add_argument(
        '-j', '--json_folder', help='folder to save dest_folder/.../books.json (default: "")', default='')
    parser.add_argument(
        '--skip_imgs', help='don\'t downloading covers', action='store_true')
    parser.add_argument(
        '--skip_txt', help='don\'t downloading txt', action='store_true')
    args = parser.parse_args()
    if args.start_page > args.end_page:
        exit('Wrong input')

    base_path = Path(args.dest_folder)
    if not args.skip_txt:
        books_path = base_path / 'books'
        books_path.mkdir(parents=True, exist_ok=True)
    if not args.skip_imgs:
        covers_path = base_path / 'images'
        covers_path.mkdir(parents=True, exist_ok=True)
    json_path = base_path / args.json_folder
    json_path.mkdir(parents=True, exist_ok=True)

    books = []
    for page_num in range(args.start_page, args.end_page + 1):
        while True:
            try:
                category_url = f'https://tululu.org/l55/{page_num}/'
                category_response = requests.get(category_url)
                category_response.raise_for_status()
                check_for_redirect(category_response,
                                   f'No page with this number')
                category_soup = BeautifulSoup(category_response.text, 'lxml')
                books_pages_soups = category_soup.select('.bookimage a')
                books_pages_urls = tuple(map(lambda x: urljoin(
                    category_response.url, x['href']), books_pages_soups))
                break
            except requests.ConnectionError:
                print('Connection problem. Reconnecting...')
                time.sleep(5)
            except requests.HTTPError as e:
                exit(e)
        print(f'Downloading page number {page_num} ...\n')
        for book_page_url in books_pages_urls:
            while True:
                try:
                    book_id = ''.join(
                        filter(lambda x: x.isdigit(), urlparse(book_page_url).path))
                    book_response = requests.get(
                        book_page_url, allow_redirects=False)
                    book_response.raise_for_status()
                    check_for_redirect(
                        book_response, f'{book_id}. No book with this ID')
                    book = parse_book_page(book_response)
                    if not args.skip_txt:
                        txt_url = 'https://tululu.org/txt.php'
                        txt_path = download_txt(
                            txt_url, book_id, book['name'], books_path)
                        book['txt_path'] = str(txt_path)
                    if book not in books:
                        books.append(book)
                    print(f'{book_id}. Downloaded "{book["name"]}"')
                    if not args.skip_imgs:
                        cover_path = download_image(
                            book['cover_url'], covers_path)
                        book['cover_path'] = str(cover_path)
                    del book['cover_url']
                    break
                except requests.ConnectionError:
                    print('Connection problem. Reconnecting...')
                    time.sleep(5)
                except requests.HTTPError as e:
                    print(e)
                    break
            print()

    with open(json_path / 'books.json', 'w', encoding='utf8') as file:
        json.dump(books, file, ensure_ascii=False)
    print('Done')


if __name__ == '__main__':
    main()
