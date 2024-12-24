# app/Dockerfile

FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gnupg2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala el controlador ODBC de Microsoft para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Copia los archivos de requerimientos y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script de Python
COPY script_dim_time.py .

# Define el comando por defecto (ya está definido en docker-compose.yml)
# CMD ["python", "script_dim_time.py"]
