FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache build-base ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt yt-dlp

COPY . .
COPY docker-entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/docker-entrypoint.sh /app/scripts/db_init.sh \
    && adduser -D -H appuser
USER appuser

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
