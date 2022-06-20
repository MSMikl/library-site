import os

from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup

def main():
    category_index = 55
    url = f"https://tululu.org/l{category_index}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    rel_img_url = (
        soup
        .find('div', id='content')
        .find_all('table', class_='d_book')[0]
        .find('a')['href']
    )
    abs_img_url = urljoin(url, rel_img_url)
    print(abs_img_url)


if __name__ == '__main__':
    main()