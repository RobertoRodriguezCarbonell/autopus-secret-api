# ==================================================
# Dockerfile - Autopus Secret API
# ==================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Autopus <info@autopus.es>"
LABEL description="API REST segura para compartir secretos con autodestrucción"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        && rm -rf /var/lib/apt/lists/*

# Copiar todo el código primero
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root para ejecutar la app
RUN useradd -m -u 1000 autopus && \
    chown -R autopus:autopus /app

# Cambiar a usuario no-root
USER autopus

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
