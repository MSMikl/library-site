import json
import os
import sys
from time import sleep
from urllib.error import HTTPError

from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup

from main import parse_book_page, download_content, check_for_redirect

def main():
    books_data = []
    book_urls = []
    category_index = 55
    for page_number in range(1, 2):
        url = f"https://tululu.org/l{category_index}/{page_number}"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_urls += [
            urljoin(url, link.find('a')['href']) for link in (
                soup
                .find('div', id='content')
                .find_all('table', class_='d_book')
                )
        ]
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
                    f'Ошибка соединения. Повторное подключение через 10 секунд',
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
        while True:
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
        book_meta['book_path'] = os.path.join('books/', book_filename)
        if book_meta.get('image_url'):
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
                        "Ошибка соединения, повторное подключение через 10 секунд",
                        file=sys.stderr()
                    )
                    sleep(10)
                    break
                break
            book_meta['img_src'] = os.path.join('images/', image_name)
        del book_meta['image_url']
        del book_meta['txt_url']
        books_data.append(book_meta)
    
    print(books_data)
    with open('books.json', 'w', encoding='UTF-8') as file:
        json.dump(books_data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
