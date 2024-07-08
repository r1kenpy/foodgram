### С foodgram можно:
- создавать и редактировать свои рецепты;
- просматривать рецепты других авторов;
- добавлять рецепты в избранное или в корзину;
- просматривать профили авторов и подписываться на них;
- скачать список покупок.
Адрес сайта: http://foooodgram.ddns.net/

### Стек:
- Python 3.9
- Django 3.2
- Django REST framework 3.12
- Nginx
- Docker
- PostgreSQL


### Как запустить:
Клонируйте репозиторий `git clone git@github.com:r1kenpy/foodgram.git`

Создайте файл .env с:
```
DEBUG=False
USE_POSTGRES=True
SECRET_KEY=<your_secret_key>
ALLOWED_HOSTS=<your_host>
POSTGRES_DB=<postgres_db_name>
POSTGRES_USER=<postgres_user>
POSTGRES_PASSWORD=<postgres_password>
DB_HOST=<postgres_db_host>
DB_PORT=5432
```

Находясь в папке infra, выполните команду `docker-compose up`. 
При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

#### backend разработка @r1kenpy