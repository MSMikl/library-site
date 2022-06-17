from pathlib import Path

import requests

Path('./books').mkdir(parents=True, exist_ok=True)

def check_for_redirect(content):
    if content.history:
        raise requests.HTTPError
    return

def main():

    for book in range(10):
        url = 'https://tululu.org/txt.php?id='
        response = requests.get(url=f'{url}{book}')
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            print(f'Книги с номером {book} не существует')
            continue

        with open (f'./books/id{book}.txt', 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    main()