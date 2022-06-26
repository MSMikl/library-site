import json
import os

from more_itertools import chunked

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    page_size = 20
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    with open('books.json', 'r', encoding='UTF-8') as file:
        books = json.load(file)
    os.makedirs('./pages', exist_ok=True)
    paged_books = list(chunked(books, page_size))
    for number, page in enumerate(paged_books):
        chunked_books = list(chunked(page, 2))
        template = env.get_template('template.html')
        rendered_page = template.render(
            books=chunked_books
        )
        with open(os.path.join(
            'pages',
            f"index{number}.html"
        ), 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    main()
