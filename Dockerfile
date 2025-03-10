FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY requirements-test.txt .

RUN pip install --no-cache-dir --upgrade pip wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-test.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY start.sh /start.sh
RUN chmod +x /start.sh

COPY . .

CMD ["/start.sh"]
