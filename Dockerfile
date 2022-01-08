# syntax=docker/dockerfile:1
FROM python:3.10-alpine AS base-image
ENV PATH="/opt/venv/bin:$PATH"
RUN apk add --no-cache mariadb-connector-c-dev

FROM base-image AS builder
RUN python -m venv /opt/venv
RUN apk add --no-cache build-base
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base-image
COPY --from=builder /opt/venv /opt/venv
COPY app /app
WORKDIR /app
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "-w 4", "-k uvicorn.workers.UvicornWorker", "-b 0.0.0.0:8000", "pick_pool.asgi:application"]
