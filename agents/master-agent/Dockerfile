FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


RUN pip install "adk>=0.0.5" --extra-index-url https://pypi.pkg.dev/google-cloud-agent-sdk/simple


COPY . .

EXPOSE 8080


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
