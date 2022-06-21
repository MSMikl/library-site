import argparse
import json
import os
import sys
from time import sleep

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup

from main import parse_book_page, download_content, check_for_redirect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        '--start_page',
        type=int,
        help='Номер первой страницы для скачивания',
        default=1
    )
    parser.add_argument(
        '-e',
        '--end_page',
        type=int,
        help='Номер последней страницы для скаичвания',
        default=1
    )
    parser.add_argument(
        '-d',
        '--dest_folder',
        type=str,
        help='Папка для скачивания',
        default='./'
    )
    parser.add_argument(
        '-si',
        '--skip_imgs',
        action='store_const',
        const=True,
        help='Не скачивать обложки'
    )
    parser.add_argument(
        '-st',
        '--skip_txt',
        action='store_const',
        const=True,
        help="Не скачивать txt"
    )
    parser.add_argument(
        '-j',
        '--json_path',
        type=str,
        default='./books.json',
        help='Путь к json-файлу с информацией'
        
    )
    args = parser.parse_args()

    Path(os.path.join('.', args.dest_folder)).mkdir(
        parents=True,
        exist_ok=True
    )
    os.chdir(os.path.join('.', args.dest_folder))
    books_data = []
    book_urls = []
    category_index = 55
    for page_number in range(args.start_page, args.end_page + 1):
        url = f"https://tululu.org/l{category_index}/{page_number}"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            break
        soup = BeautifulSoup(response.text, 'lxml')
        book_url_selector = "#content table.d_book a[href^='/b']"
        book_urls += [
            urljoin(
                url,
                link['href']
                ) for link in soup.select(book_url_selector)
        ]
    print(f'Собрано {len(book_urls)} книг. Начинаю скачивание')
    for book_url in book_urls:
        skip_book = False
        while True:
            try:
                response = requests.get(book_url)
                response.raise_for_status()
                check_for_redirect(response)
                book_meta = parse_book_page(response)
            except requests.HTTPError:
                print(f'Книги {book_url} не существует', file=sys.stderr)
                skip_book = True
                break
            except requests.ConnectionError:
                print(
                    'Ошибка соединения. Повторное подключение через 10с',
                    file=sys.stderr
                )
                sleep(10)
                break
            if not book_meta.get('txt_url'):
                skip_book = True
            break
        if skip_book:
            continue
        txt_url = urljoin(book_url, book_meta['txt_url'])
        book_filename = f"{(book_meta['title'])}.txt"
        while not args.skip_txt:
            try:
                download_content(txt_url, book_filename, 'books/')
            except requests.HTTPError:
                print(
                    f"TXT-файла книги {book_filename} не существует",
                    file=sys.stderr
                )
                skip_book = True
                break
            except requests.ConnectionError:
                print(
                    "Ошибка соединение, повторное подключение через 10 секунд",
                    file=sys.stderr()
                )
                sleep(10)
                break
            break
        if skip_book:
            continue
        if not args.skip_txt:
            book_meta['book_path'] = os.path.join('books/', book_filename)
        
        if book_meta.get('image_url') and not args.skip_imgs:
            image_url = urljoin(book_url, book_meta['image_url'])
            image_name = book_meta['image_url'].split('/')[-1]
            while True:
                try:
                    download_content(image_url, image_name, 'images/')
                except requests.HTTPError:
                    print(
                        f"Картинки {book_meta['image_url']} не существует",
                        file=sys.stderr
                    )
                    break
                except requests.ConnectionError:
                    print(
                        "Ошибка соединения, повторное подключение через 10с",
                        file=sys.stderr()
                    )
                    sleep(10)
                    break
                break
            book_meta['img_src'] = os.path.join('images/', image_name)
        del book_meta['image_url']
        del book_meta['txt_url']
        books_data.append(book_meta)

    with open(os.path.join('.', args.json_path), 'w', encoding='UTF-8') as file:
        json.dump(books_data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
