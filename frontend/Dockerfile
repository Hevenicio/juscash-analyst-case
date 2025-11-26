FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY frontend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/src /app

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"]