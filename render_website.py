import json
import os
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def rebuild_pages():
    page_size = 20
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    with open('books.json', 'r', encoding='UTF-8') as file:
        books = json.load(file)
    os.makedirs('./pages', exist_ok=True)
    paged_books = list(chunked(books, page_size))
    total_pages = len(paged_books)
    for page_number, page in enumerate(paged_books):
        chunked_books = list(chunked(page, 2))
        template = env.get_template('template.html')
        rendered_page = template.render(
            books=chunked_books,
            total_pages=total_pages + 1,
            current_page=page_number + 1
        )
        with open(os.path.join(
            'pages',
            f"index{page_number + 1}.html"
        ), 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    rebuild_pages()
    server = Server()
    server.watch('template.html', rebuild_pages())
    server.serve(root='.')


if __name__ == '__main__':
    main()
