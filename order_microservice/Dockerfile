FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=off

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]