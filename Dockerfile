FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY twin/ ./twin/
COPY kb/ ./kb/

ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]
