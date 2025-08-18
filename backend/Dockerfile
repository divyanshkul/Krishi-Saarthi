# Use Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

RUN mkdir -p output

EXPOSE 8000

CMD ["python", "main.py"]