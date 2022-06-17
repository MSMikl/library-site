from pathlib import Path

import requests

Path('./books').mkdir(parents=True, exist_ok=True)

for book in range(10):
    url = 'https://tululu.org/txt.php?id='
    response = requests.get(url=f'{url}{book}')
    response.raise_for_status()

    with open (f'./books/id{book}.txt', 'wb') as file:
        file.write(response.content)
