# Cкачивание книг

Библиотека предназначена для скачивания текстов книг и информации о них с сайта https://tululu.org/.

## Установка

Для использования библиотеки необходим **Python** версии не ниже 3.5.

Скачайте содержимое репозитория на компьютер, установите зависимости, выполнив

        pip install -r requirements.txt

## Использование

### main.py

Скрипт скачивает книги по порядку номеров в библиотеке.

Запустите скрипт командой

        python main.py [-s] [-e]

Параметры **-s** и  **-e** обозначают начальный и конечный номера книг в библиотеке для скачивания.

Скрипт скачивает текстовые файлы книг с соответствующими названиями в папку `books`, обложки книг (при их наличии) скачиваются в папку `images`.

### parse_tululu_category.py

Продвинутая версия скрипта - скачивает книги в жанре "Научная фантастика", обложки к ним (при наличии), а также создает json-файл с информацией о скачанных книгах.

Запустите скрипт командой

        parse_tululu_category.py [-h] [-s START_PAGE] [-e END_PAGE] [-d DEST_FOLDER] [-si] [-st] [-j JSON_PATH]

Параметры запуска

        -s START_PAGE, --start_page START_PAGE          Номер первой страницы списка книг в жанре для скачивания (по умолчанию 1)
        -e END_PAGE, --end_page END_PAGE                Номер последней страницы для скачивания (по умолчанию 1)
        -d DEST_FOLDER, --dest_folder DEST_FOLDER       Папка для скачивания (По умолчанию - папка с программой)
        -si, --skip_imgs                                Не скачивать обложки
        -st, --skip_txt                                 Не скачивать txt
        -j JSON_PATH, --json_path JSON_PATH             Путь к json-файлу с информацией (по умолчанию - books.json в папке с программой)
