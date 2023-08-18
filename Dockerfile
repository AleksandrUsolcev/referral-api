FROM python:3.9.17-slim

WORKDIR /app

COPY /referral /app/

COPY pyproject.toml poetry.lock entrypoint.sh ./

RUN pip3 install poetry

RUN poetry config virtualenvs.create false

RUN poetry install

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]
