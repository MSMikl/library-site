import argparse
import os
import sys

from pathlib import Path
from time import sleep
from urllib.parse import urljoin, urlparse

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(content):
    if content.history:
        raise requests.HTTPError
    return


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')
    title = sanitize_filename(soup.find('h1').text.split('::')[0].strip())
    author = sanitize_filename(soup.find('h1').find('a').text)
    image_url = urljoin(
        'https://tululu.org/',
        soup.find(class_='bookimage').find('img')['src']
    )
    comments = [
        x.find('span', class_='black').text for x in (
            soup.find_all('div', class_='texts')
        )
    ]
    genres = [x.text for x in soup.find('span', class_='d_book').find_all('a')]
    return {
        'author': author,
        'title': title,
        'image_url': image_url,
        'comments': comments,
        'genres': genres
    }


def download_content(url, filename, folder):
    response = requests.get(url)
    response.raise_for_status()
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        '--start_id',
        type=int,
        help='Начальный номер книги для скачивания',
        default=0
    )
    parser.add_argument(
        '-e',
        '--end_id',
        type=int,
        help='Последний номер книги для скачивания',
        default=10
    )
    args = parser.parse_args()
    Path('books/').mkdir(parents=True, exist_ok=True)

    txt_url = 'https://tululu.org/txt.php'

    for book in range(args.start_id, args.end_id):
        params = {'id': book}
        while True:
            try:
                txt_response = requests.get(txt_url, params=params)
                txt_response.raise_for_status()
                check_for_redirect(txt_response)
            except requests.HTTPError:
                print(f'Книги {book} не существует', file=sys.stderr)
                skip_book = True
                break
            except requests.ConnectionError:
                print(
                    'Ошибка соединения, повторная попытка через 10 секунд',
                    file=sys.stderr
                )
                sleep(10)
                continue
            skip_book = False
            break
        if skip_book:
            continue

        book_page_url = f'https://tululu.org/b{book}/'

        while True:
            try:
                book_page_response = requests.get(book_page_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)
            except requests.HTTPError:
                print(
                    f'Страницы {book_page_url} не существует',
                    file=sys.stderr
                )
                book += 1
                skip_book = True
                break
            except requests.ConnectionError:
                print(
                    'Ошибка соединения, повторная попытка через 10 секунд',
                    file=sys.stderr
                )
                sleep(10)
                continue
            skip_book = False
            break
        if skip_book:
            continue

        book_meta = parse_book_page(book_page_response)
        filename = f"{book}. {sanitize_filename(book_meta['title'])}.txt"
        with open(os.path.join('books/', filename), 'wb') as file:
            file.write(txt_response.content)
        book += 1
        image_name = urlparse(book_meta['image_url']).path.split('/')[-1]
        if image_name != 'nopic.gif':
            try:
                download_content(book_meta['image_url'], image_name, 'images/')
            except requests.HTTPError:
                print(
                    f"Картинки {book_meta['image_url']} не существует",
                    file=sys.stderr
                )
                continue
            except requests.ConnectionError:
                continue


if __name__ == '__main__':
    main()
