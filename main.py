import requests
from pathlib import Path

books_path = Path('books')
books_path.mkdir(exist_ok=True)
for book_id in range(1, 6):
    url = f'https://tululu.org/txt.php?id={book_id}'

    response = requests.get(url)
    response.raise_for_status()

    with open(books_path / f'{book_id}.txt', 'wb') as file:
        file.write(response.content)
