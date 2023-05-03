import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def parse_book_page(book_id):
    book_page_url = f'https://tululu.org/b{book_id}/'
    book_response = requests.get(book_page_url, allow_redirects=False)
    book_response.raise_for_status()
    check_for_redirect(book_response, f'{book_id}. No book with this ID')
    book_soup = BeautifulSoup(book_response.text, 'lxml')           
    book_title = book_soup.find('td', class_='ow_px_td').find('h1').text
    book_name, book_author = map(str.strip, book_title.split('::'))
    sanitized_book_name = sanitize_filename(book_name)
    cover_web_path = book_soup.find('div', class_='bookimage').find('img')['src']
    cover_url = urljoin('https://tululu.org/', cover_web_path)
    book_comments = book_soup.find('td', class_='ow_px_td').find_all('span', class_='black')
    book_genres = tuple(map(lambda x: x.text, book_soup.find('span', class_='d_book').find_all('a')))
    txt_url = f'https://tululu.org/txt.php?id={book_id}'

    return {
        'name': sanitized_book_name,
        'author': book_author,
        'txt_url': txt_url,
        'page_url': book_page_url,
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
        return
    image_response = requests.get(image_url, allow_redirects=False)
    image_response.raise_for_status()
    check_for_redirect(image_response, f'Can\'t download "{image_name}"')
    with open(image_full_path, 'wb') as file:
        file.write(image_response.content)


def download_txt(txt_url, txt_id, txt_name, txt_path):
    txt_full_path = txt_path / f'{txt_id}. {txt_name}.txt'
    if txt_full_path.is_file():
        return
    txt_response = requests.get(txt_url, allow_redirects=False)
    txt_response.raise_for_status()
    check_for_redirect(txt_response, f'{txt_id}. Can\'t download "{txt_name}"')
    with open(txt_full_path, 'wb') as file:
        file.write(txt_response.content)


def download_comments(book_comments, book_id, comments_path):
    comments_full_path = comments_path / f'{book_id}.txt'
    if not book_comments or comments_full_path.is_file():
        return
    with open(comments_path / f'{book_id}.txt', 'wt', encoding='utf-8') as file:
        for comment in book_comments:
            file.write(f'{comment.text}\n')


def main():
    print('Downloading...', end='\n\n')
    books_path = Path('books')
    books_path.mkdir(exist_ok=True)
    covers_path = Path('images')
    covers_path.mkdir(exist_ok=True)
    comments_path = Path('comments')
    comments_path.mkdir(exist_ok=True)
    for book_id in range(1, 11):
        try:
            book = parse_book_page(book_id)
            download_txt(book['txt_url'], book_id, book['name'], books_path)
            print(f'{book_id}. Downloaded "{book["name"]}"')  
            print(f'Author: {book["author"]}')
            print(f'Genre: {book["genres"]}')
            download_comments(book['comments'], book_id, comments_path)    
            download_image(book['cover_url'], covers_path)             
        except requests.HTTPError as e:
            print(e)
        print()    
    print('Done')


if __name__ == '__main__':
    main()