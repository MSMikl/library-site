import os
from pathlib import Path

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(content):
    if content.history:
        raise requests.HTTPError
    return


def get_book_meta(id):
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title = sanitize_filename(soup.find('h1').text.split('::')[0].strip())
    author = sanitize_filename(soup.find('h1').find('a').text)
    return {'author': author, 'title': title}


def download_txt(book_id, filename, folder='books/'):
    url = f'https://tululu.org/txt.php?id={book_id}'
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return
    book_meta = get_book_meta(book_id)
    filename = f"{book_id}. {sanitize_filename(book_meta['title'])}.txt"
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)
    return True


def main():
    for book in range(1, 11):        
        download_txt(book, 'books/')

if __name__ == '__main__':
    main()