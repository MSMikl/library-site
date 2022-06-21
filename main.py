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
    title = sanitize_filename(soup.select_one("h1").text.split('::')[0].strip())
    author = sanitize_filename(soup.select_one("h1 a").text)
    image_url = soup.select_one(".bookimage img")['src']
    comments = [
        texts_class.text for texts_class in (
            soup.select(".texts .black")
        )
    ]
    genres = [
        link.text for link in soup.select(".d_book a[href^='/l']")
        ]
    txt_url = soup.select_one(".d_book a[href^='/txt']")
    return {
        'author': author,
        'title': title,
        'image_url': image_url if image_url != '/images/nopic.gif' else None,
        'comments': comments,
        'genres': genres,
        'txt_url': txt_url['href'] if txt_url else None
    }


def download_content(url, filename, folder,  params=None):
    response = requests.get(url=url, params=params)
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

        params = {'id': book_id}
        filename = f"{book_id}. {(book_meta['title'])}.txt"
        while True:
            try:
                download_content(txt_url, filename, 'books/', params=params)
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

        if not book_meta.get('image_url'):
            continue
        image_name = book_meta['image_url'].split('/')[-1]
        image_url = urljoin(book_page_url, book_meta['image_url'])
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
