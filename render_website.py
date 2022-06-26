from livereload import Server, shell


def main():

    server = Server()
    server.watch('template.html', shell('./venv/Scripts/python.exe on_reload.py'))
    server.serve(root='.')


if __name__ == '__main__':
    main()
