from pathlib import Path

import requests

from bs4 import BeautifulSoup

Path('./books').mkdir(parents=True, exist_ok=True)

def check_for_redirect(content):
    if content.history:
        raise requests.HTTPError
    return


def get_book_meta(id):
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text.split('::')[0].strip()
    author = soup.find('h1').find('a').text
    return {'author': author, 'title': title}


def main():
    for book in range(10):
        url = f'https://tululu.org/txt.php?id={book}'
        response = requests.get(url=url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            print(f'Книги с номером {book} не существует')
            continue
        book_meta = get_book_meta(book)

        with open (f"./books/{book_meta['author']} - {book_meta['title']}.txt", 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    main()