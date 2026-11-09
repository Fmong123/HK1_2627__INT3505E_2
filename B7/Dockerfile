FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home app \
    && mkdir -p /data /app/instance && chown app:app /data /app/instance
COPY --chown=app:app . .
ENV DB_URL=sqlite:////data/lab7.db PYTHONUNBUFFERED=1
USER app
EXPOSE 5000
CMD ["sh", "-c", "flask --app app init-db && gunicorn --bind 0.0.0.0:5000 --workers 1 app:app"]
