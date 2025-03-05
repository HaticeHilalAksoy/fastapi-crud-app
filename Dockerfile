# Python resmi imajı kullanılıyor
FROM python:3.11

# Çalışma dizini oluşturuluyor
WORKDIR /app

# Bağımlılıklar yükleniyor
COPY requirements.txt .

# Eksik wheel ve pip güncellemelerini yükleyelim
RUN pip install --no-cache-dir --upgrade pip wheel

# Projenin bağımlılıklarını yükleyelim
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları ekleniyor
COPY . .

# FastAPI uygulamasını başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
