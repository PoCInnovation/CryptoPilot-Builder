FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY run_mcp.sh .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2-binary sqlalchemy

RUN chmod +x run_mcp.sh

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["./run_mcp.sh"]
