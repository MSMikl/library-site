import os
import sys

from livereload import Server, shell


def main():
    exec_path = sys.executable.replace(os.sep, '/')
    print(exec_path)
    server = Server()
    server.watch('template.html', shell(f'{exec_path} on_reload.py'))
    server.serve(root='.')


if __name__ == '__main__':
    main()
