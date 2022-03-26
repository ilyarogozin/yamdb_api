FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .

ENV DB_ENGINE="django.db.backends.postgresql"
ENV DB_NAME=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV DB_HOST=db
ENV DB_PORT=5432
ENV ALLOWED_HOSTS="51.250.70.25"

RUN apt update
RUN apt install -y libpq-dev
RUN apt install -y gcc
RUN apt install nano && touch ~/.nanorc && echo include "/usr/share/nano/python.nanorc" >> ~/.nanorc

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
