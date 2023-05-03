import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def check_for_redirect(response, error_msg):
    if response.is_redirect:
        raise requests.HTTPError(error_msg)


def download_image(image_url, image_path):
    image_response = requests.get(image_url, allow_redirects=False)
    image_response.raise_for_status()
    *_, image_name = urlparse(image_url).path.split('/')
    check_for_redirect(image_response, f'Can\'t download "{image_name}"')
    image_full_path = image_path / image_name
    if image_full_path.is_file():
        return
    with open(image_full_path, 'wb') as file:
        file.write(image_response.content)


def download_txt(txt_url, txt_id, txt_name, txt_path):
    txt_response = requests.get(txt_url, allow_redirects=False)
    txt_response.raise_for_status()
    check_for_redirect(txt_response, f'Can\'t download "{txt_name}.txt"')
    txt_full_path = txt_path / f'{txt_id}. {txt_name}.txt'
    if txt_full_path.is_file():
        return
    with open(txt_full_path, 'wb') as file:
        file.write(txt_response.content)


def main():
    print('Downloading...')
    books_path = Path('books')
    books_path.mkdir(exist_ok=True)
    covers_path = Path('images')
    covers_path.mkdir(exist_ok=True)
    for book_id in range(1, 11):
        try:
            book_url = f'https://tululu.org/b{book_id}/'
            book_response = requests.get(book_url, allow_redirects=False)
            book_response.raise_for_status()
            check_for_redirect(book_response, f'No book with id: {book_id}')
            book_soup = BeautifulSoup(book_response.text, 'lxml')
            book_title = book_soup.find('td', class_='ow_px_td').find('h1').text
            book_name, *_ = map(str.strip, book_title.split('::'))
            sanitized_book_name = sanitize_filename(book_name)
            txt_url = f'https://tululu.org/txt.php?id={book_id}'
            download_txt(txt_url, book_id, sanitized_book_name, books_path)
            print(f'Downloaded "{sanitized_book_name}.txt"')
            cover_web_path = book_soup.find('div', class_='bookimage').find('img')['src']
            cover_url = urljoin('https://tululu.org/', cover_web_path)
            download_image(cover_url, covers_path)         
        except requests.HTTPError as e:
            print(e)
    print('The END')


if __name__ == '__main__':
    main()