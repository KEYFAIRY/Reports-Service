# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Instalar dependencias del sistema para compilar mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente
COPY . .

# Comando por defecto al iniciar el contenedor
CMD ["python", "-m", "app.main"]