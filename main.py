import os
from pathlib import Path
from urllib.parse import urljoin, urlparse

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
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title = sanitize_filename(soup.find('h1').text.split('::')[0].strip())
    author = sanitize_filename(soup.find('h1').find('a').text)
    image_url = urljoin(
        'https://tululu.org/',
        soup.find(class_='bookimage').find('img')['src']
    )
    comments = [
        x.find('span', class_='black').text for x in soup.find_all('div', class_='texts')
    ]
    print(comments)
    return {
        'author': author,
        'title': title,
        'image_url': image_url,
        'comments': comments
    }


def download_content(url, filename, folder):
    response = requests.get(url)
    response.raise_for_status()
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def main():
    Path('books/').mkdir(parents=True, exist_ok=True)
    for book in range(1, 11):
        url = f'https://tululu.org/txt.php?id={book}'
        response = requests.get(url)
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        book_meta = get_book_meta(book)
        filename = f"{book}. {sanitize_filename(book_meta['title'])}.txt"
        with open(os.path.join('books/', filename), 'wb') as file:
            file.write(response.content)
        image_name = urlparse(book_meta['image_url']).path.split('/')[-1]
        if image_name != 'nopic.gif':
            download_content(book_meta['image_url'], image_name, 'images/')

if __name__ == '__main__':
    main()