FROM python:3.7-slim

WORKDIR /app

COPY . .

ENV SECRET_KEY="p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs"
ENV DB_ENGINE="django.db.backends.postgresql"
ENV DB_NAME=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=123456
ENV DB_HOST=db
ENV DB_PORT=5432

RUN apt update
RUN apt install -y libpq-dev
RUN apt install -y gcc
RUN apt install nano && touch ~/.nanorc && echo include "/usr/share/nano/python.nanorc" >> ~/.nanorc
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
