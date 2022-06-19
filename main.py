import argparse
import logging
import os
import sys

from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

logger = logging.getLogger('log_file')


def check_for_redirect(content):
    if content.history:
        raise requests.HTTPError


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')
    title = sanitize_filename(soup.find('h1').text.split('::')[0].strip())
    author = sanitize_filename(soup.find('h1').find('a').text)
    image_url = soup.find(class_='bookimage').find('img')['src']
    comments = [
        texts_class.find('span', class_='black').text for texts_class in (
            soup.find_all('div', class_='texts')
        )
    ]
    genres = [
        link.text for link in soup.find('span', class_='d_book').find_all('a')
        ]
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
    check_for_redirect(response)
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def main():
    log_handler = RotatingFileHandler(
        'app.log',
        maxBytes=30000,
        backupCount=2
    )
    log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s'))
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

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

    for book_id in range(args.start_id, args.end_id):
        params = {'id': book_id}
        while True:
            try:
                txt_response = requests.get(txt_url, params=params)
                txt_response.raise_for_status()
                check_for_redirect(txt_response)
            except requests.HTTPError as err:
                logger.exception(err, exc_info=True)
                print(f'Книги {book_id} не существует', file=sys.stderr)
                skip_book = True
                break
            except requests.ConnectionError as err:
                logger.exception(err, exc_info=True)
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

        book_page_url = f'https://tululu.org/b{book_id}/'

        while True:
            try:
                book_page_response = requests.get(book_page_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)
            except requests.HTTPError as err:
                logger.exception(err, exc_info=True)
                print(
                    f'Страницы {book_page_url} не существует',
                    file=sys.stderr
                )
                skip_book = True
                break
            except requests.ConnectionError as err:
                logger.exception(err, exc_info=True)
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
        filename = f"{book_id}. {sanitize_filename(book_meta['title'])}.txt"
        with open(os.path.join('books/', filename), 'wb') as file:
            file.write(txt_response.content)
        image_name = book_meta['image_url'].split('/')[-1]
        image_url = urljoin(book_page_url, book_meta['image_url'])
        if image_name != 'nopic.gif':
            try:
                download_content(image_url, image_name, 'images/')
            except requests.HTTPError as err:
                logger.exception(err, exc_info=True)
                print(
                    f"Картинки {image_url} не существует",
                    file=sys.stderr
                )
                continue
            except requests.ConnectionError as err:
                logger.exception(err, exc_info=True)
                continue


if __name__ == '__main__':
    main()
