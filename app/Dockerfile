FROM python:3.12-slim

WORKDIR /app

# Flask + OpenTelemetry .
RUN pip install --no-cache-dir flask opentelemetry-distro opentelemetry-exporter-otlp \
    && opentelemetry-bootstrap -a install

COPY app.py .

ENV FLASK_APP=app.py
EXPOSE 5000

# `opentelemetry-instrument` wraps the app and auto-generates traces, metrics,
# and logs — no SDK code in app.py required.
CMD ["opentelemetry-instrument", "flask", "run", "--host=0.0.0.0", "--port=5000"]
