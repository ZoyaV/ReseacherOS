FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY hub/requirements.txt hub/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r hub/requirements.txt

COPY koi koi
COPY web web
COPY hub hub

ENV PYTHONPATH=/app
EXPOSE 8080

CMD ["uvicorn", "hub.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
