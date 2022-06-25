from livereload import Server, shell


def main():

    server = Server()
    server.watch('template.html', shell('python on_reload.py'))
    server.serve(root='.')


if __name__ == '__main__':
    main()
