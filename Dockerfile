FROM python:3.12-slim

ENV APP_HOME /app

WORKDIR $APP_HOME

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . /app

EXPOSE 3000

CMD ["poetry", "run", "python", "web_service/main.py"]