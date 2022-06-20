import os

from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup


def main():
    book_urls = []
    category_index = 55
    for page_number in range(1, 11):
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
    print(book_urls)


if __name__ == '__main__':
    main()
