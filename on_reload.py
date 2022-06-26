import json

from more_itertools import chunked

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    with open('books.json', 'r', encoding='UTF-8') as file:
        books = json.load(file)

    chunked_books = list(chunked(books, 2))
    print(len(chunked_books[0]))

    template = env.get_template('template.html')

    rendered_page = template.render(
        books=chunked_books
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    main()
