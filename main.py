import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.is_redirect:
        raise requests.HTTPError("It's not a book")


def download_book(book_id, book_path):
    bookpage_url = f'https://tululu.org/b{book_id}/'
    bookpage_response = requests.get(bookpage_url, allow_redirects=False)
    bookpage_response.raise_for_status()
    check_for_redirect(bookpage_response)
    soup = BeautifulSoup(bookpage_response.text, 'lxml')
    title_text = soup.find('td', class_='ow_px_td').find('h1').text
    book_name, *_ = map(str.strip, title_text.split('::'))
    sanitized_book_name = sanitize_filename(book_name)
    book_url = f'https://tululu.org/txt.php?id={book_id}'
    book_response = requests.get(book_url)
    book_response.raise_for_status()
    check_for_redirect(book_response)
    with open(book_path / f'{book_id}. {sanitized_book_name}.txt', 'wb') as file:
        file.write(book_response.content)

def main():
    books_path = Path('books')
    books_path.mkdir(exist_ok=True)

    for book_id in range(1, 11):
        try:
            download_book(book_id, books_path)         
        except requests.HTTPError as e:
            print(e)


if __name__ == '__main__':
    main()