# homework_bot
python telegram bot Проверяет статус отправленного задания на код-ревью с помощью API.


## Установка

Клонируйте проект
```sh
cd dev
mkdir homework_bot
git clone git@github.com:imsemin/book-catalog.git
```

Установите виртуальное окружение и зависимости

```sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
В папке проекта создайте файл
#### **.env**

С указанием следующих переменных
```sh
TOKEN_PRAKT - токен praktikum.yandex
TOKEN_TEL - токен телеграмма
CHAT_ID - номер чата
```

### Авторы

Yandex Praktikum and Evgeniy Semin
