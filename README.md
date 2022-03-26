![Actions Status](https://github.com/ilyarogozin/yamdb/actions/workflows/yamdb_workflow.yml/badge.svg)
# YAMDB_API
## yamdb_api - это проект API для сервиса отзывов к произведениям
### Авторы:
- Ilya Rogozin https://github.com/ilyarogozin
### Технологии:
- Python 3
- Django 2
- DRF
- Docker

# Как запустить проект:
- Установите Docker, инструкция:
https://docs.docker.com/get-docker/

- Установите docker-compose, инструкция:
https://docs.docker.com/compose/install/

- Клонируйте репозиторий:
```
git clone git@github.com:ilyarogozin/yamdb_api.git
```

- Перейдите в папку с файлом docker-compose:
```
cd yamdb_api/infra
```

- Создайте в этой папке файл окружения .env, который будет содержать:
```
SECRET_KEY="p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs"
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456
DB_HOST=db
DB_PORT=5432
```

- Соберите контейнеры и запустите их:
```
docker-compose up
```

#### Установите подсветку синтаксиса терминала bash:
- Откройте конфигурационный файл:
```
nano /etc/skel/.bashrc
```
- Раскомментите строку __force_color_prompt=yes__
- Примените изменения:
```
source /etc/skel/.bashrc
```
-----------------------------------------------------

- Выполните миграции:
```
docker-compose exec web python manage.py migrate
```

- Создайте суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```

- Соберите статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```

- Заполните БД начальными данными:
```
docker-compose exec web python manage.py loaddata fixtures.json
```

## Примеры запросов к API можно посмотреть по запросу:
http://51.250.70.25/redoc/
