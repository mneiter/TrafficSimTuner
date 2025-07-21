# master/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY ./app ./app
COPY ./templates ./templates
COPY ./static ./static

RUN pip install --no-cache-dir fastapi uvicorn jinja2 python-multipart pydantic docker

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
