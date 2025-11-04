# 🔐 Autopus Secret API

API REST segura y autohosteada para compartir información sensible con acceso único y autodestrucción programada.

## 📋 Descripción

**Autopus Secret API** es un servicio privado que permite compartir contraseñas, claves API o cualquier información sensible de forma segura entre equipos o clientes, sin depender de terceros. Los secretos se cifran con AES-256, tienen acceso único y se autodestruyen después de ser leídos o al expirar.

### ✨ Características principales

- 🔒 **Cifrado fuerte**: AES-256 (Fernet) antes de almacenar
- 👁️ **Acceso único**: Los secretos solo pueden leerse una vez
- ⏰ **Expiración automática**: TTL configurable (5 min - 7 días)
- 🔑 **Passphrase opcional**: Protección adicional con contraseña
- 🚀 **Autohosteado**: Control total sobre tus datos
- 🧹 **Limpieza automática**: Eliminación programada de secretos expirados
- 📡 **API REST**: Fácil integración con n8n, Postman, etc.

## 🛠️ Stack Tecnológico

- **Lenguaje**: Python 3.9+
- **Framework**: FastAPI
- **Base de datos**: Supabase (PostgreSQL)
- **Cifrado**: cryptography (Fernet/AES-256) + bcrypt
- **Scheduler**: APScheduler
- **Servidor**: Uvicorn

## 📦 Instalación

### Requisitos previos

- Python 3.9 o superior
- Cuenta de Supabase (gratuita)
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/autopus-secret-api.git
cd autopus-secret-api
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus credenciales
```

#### Generar claves necesarias:

```bash
# Generar ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generar API_KEY_ADMIN
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Configurar Supabase

1. Crear un proyecto en [supabase.com](https://supabase.com)
2. Copiar la URL y API Key (anon/public)
3. Ejecutar el script SQL para crear la tabla `secrets` (próximamente en Paso 2)

## 🚀 Uso

### Iniciar el servidor

```bash
# Modo desarrollo (con auto-reload)
python app/main.py

# O con uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Endpoint raíz**: http://localhost:8000/

### Endpoints disponibles

#### Públicos (sin autenticación)

- `POST /api/secret` - Crear un nuevo secreto
- `GET /api/secret/{token}` - Leer y destruir un secreto
- `DELETE /api/secret/{token}/delete` - Destruir manualmente un secreto
- `POST /api/secret/verify` - Verificar passphrase sin revelar contenido

#### Administrativos (requieren API Key)

- `GET /api/stats` - Estadísticas del sistema
- `DELETE /api/system/purge` - Forzar limpieza de expirados
- `GET /api/system/health` - Estado del sistema
- `GET /api/system/info` - Información de versión y uptime

### Ejemplo de uso con curl

```bash
# Crear un secreto
curl -X POST "http://localhost:8000/api/secret" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Mi contraseña secreta",
    "ttl_minutes": 60,
    "passphrase": "mi-password"
  }'

# Respuesta:
# {
#   "token": "abc123...",
#   "url": "http://localhost:8000/api/secret/abc123...",
#   "expires_at": "2025-11-04T15:00:00Z",
#   "has_passphrase": true
# }

# Leer el secreto (solo funciona una vez)
curl "http://localhost:8000/api/secret/abc123..."

# Endpoint admin (con API Key)
curl "http://localhost:8000/api/stats" \
  -H "Authorization: Bearer tu-api-key-admin"
```

## 📁 Estructura del Proyecto

```
autopus-secret-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Configuración centralizada
│   ├── routers/             # Endpoints
│   │   ├── secrets.py       # Endpoints públicos
│   │   └── admin.py         # Endpoints administrativos
│   ├── models/              # Modelos de dominio
│   │   └── secret.py
│   ├── services/            # Lógica de negocio
│   │   ├── encryption.py    # Servicio de cifrado
│   │   ├── database.py      # Cliente Supabase
│   │   └── scheduler.py     # Limpieza automática (Paso 4)
│   ├── schemas/             # DTOs y validación
│   │   └── secret.py
│   └── utils/               # Utilidades
│       ├── token_generator.py
│       └── validators.py
├── tests/                   # Tests (próximamente)
├── .env.example             # Plantilla de variables
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔒 Seguridad

- ✅ Cifrado AES-256 (Fernet) de todos los secretos
- ✅ Tokens seguros generados con `secrets` module
- ✅ Hash bcrypt para passphrases
- ✅ API Key para endpoints administrativos
- ✅ HTTPS obligatorio en producción
- ✅ Sin almacenamiento de texto plano
- ✅ Sin logs de información sensible
- ✅ Validación estricta de entradas

## 🗺️ Roadmap

### ✅ Paso 1: Estructura Inicial (Completado)
- Estructura de carpetas y archivos base
- Configuración de dependencias
- FastAPI inicial con routers

### ✅ Paso 2: Configuración de Supabase (Completado)
- Diseño de esquema de base de datos
- Configuración de RLS
- Cliente Supabase operativo

### ✅ Paso 3: Implementación del Core (Completado)
- Sistema de cifrado completo
- Endpoints de crear/leer/destruir secretos
- Validación de passphrases

### ✅ Paso 4: Funcionalidades Avanzadas (Completado)
- ✅ APScheduler para limpieza automática cada hora
- ✅ Endpoints administrativos (`/admin/stats`, `/admin/system/*`)
- ✅ Security Middleware (Rate Limiting 60 req/min, Security Headers)
- ✅ Tests unitarios (pytest) para encryption, validators y token_generator
- ✅ Documentación actualizada

## 🐛 Estado Actual

**Versión**: 1.0.0 (Beta)

**Pasos completados**: 1, 2, 3, 4 ✅

La API está completamente funcional con:
- ✅ Cifrado AES-256 operativo
- ✅ Gestión completa de secretos (crear, leer, destruir)
- ✅ Passphrase protection con bcrypt
- ✅ Limpieza automática programada
- ✅ Endpoints administrativos
- ✅ Security middleware (rate limiting + headers)
- ✅ Tests unitarios verificados (25/25 pasando)

## � Ejemplos Avanzados

### Uso con Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Crear secreto con passphrase
response = requests.post(
    f"{BASE_URL}/api/secret",
    json={
        "content": "AWS_ACCESS_KEY=AKIA...",
        "ttl_minutes": 120,
        "passphrase": "mi-password-segura"
    }
)
secret_data = response.json()
print(f"Token: {secret_data['token']}")
print(f"Expira: {secret_data['expires_at']}")

# Verificar passphrase antes de leer
verify_response = requests.post(
    f"{BASE_URL}/api/secret/verify",
    json={
        "token": secret_data['token'],
        "passphrase": "mi-password-segura"
    }
)
if verify_response.json()["valid"]:
    # Leer secreto (solo funciona una vez)
    secret_response = requests.get(
        f"{BASE_URL}/api/secret/{secret_data['token']}",
        params={"passphrase": "mi-password-segura"}
    )
    print(f"Contenido: {secret_response.json()['content']}")
```

### Uso desde n8n

**Webhook para crear secreto**:
```json
{
  "method": "POST",
  "url": "http://localhost:8000/api/secret",
  "body": {
    "content": "{{$json.sensitive_data}}",
    "ttl_minutes": 60
  }
}
```

**Respuesta automática por email/chat con URL**:
```
Aquí está tu secreto temporal:
{{$json.url}}

⚠️ Solo puedes abrirlo UNA VEZ
⏰ Expira en {{$json.ttl_minutes}} minutos
```

### Endpoints Administrativos

```bash
# Ver estadísticas
curl "http://localhost:8000/admin/stats" \
  -H "X-API-Key: tu-api-key-admin"

# Health check
curl "http://localhost:8000/admin/system/health" \
  -H "X-API-Key: tu-api-key-admin"

# Información del sistema
curl "http://localhost:8000/admin/system/info" \
  -H "X-API-Key: tu-api-key-admin"

# Forzar limpieza de expirados
curl -X DELETE "http://localhost:8000/admin/system/purge" \
  -H "X-API-Key: tu-api-key-admin"
```

## 🚀 Deployment

### Opción 1: Docker (Recomendado)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t autopus-secret-api .
docker run -d -p 8000:8000 --env-file .env autopus-secret-api
```

### Opción 2: Render/Railway

1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Opción 3: VPS (Ubuntu)

```bash
# Instalar dependencias
sudo apt update
sudo apt install python3-pip python3-venv nginx certbot

# Clonar y configurar
git clone https://github.com/tu-usuario/autopus-secret-api.git
cd autopus-secret-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear servicio systemd
sudo nano /etc/systemd/system/autopus-secret.service
```

**Contenido del servicio**:
```ini
[Unit]
Description=Autopus Secret API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/usuario/autopus-secret-api
Environment="PATH=/home/usuario/autopus-secret-api/venv/bin"
ExecStart=/home/usuario/autopus-secret-api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activar servicio
sudo systemctl daemon-reload
sudo systemctl enable autopus-secret.service
sudo systemctl start autopus-secret.service

# Configurar Nginx como reverse proxy
sudo nano /etc/nginx/sites-available/autopus-secret
```

**Configuración Nginx**:
```nginx
server {
    listen 80;
    server_name secret.autopus.es;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activar sitio y certificado SSL
sudo ln -s /etc/nginx/sites-available/autopus-secret /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d secret.autopus.es
```

## 🧪 Testing

```bash
# Ejecutar todos los tests unitarios
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=app --cov-report=html

# Ejecutar tests específicos
pytest tests/test_encryption.py -v
pytest tests/test_validators.py -v
pytest tests/test_token_generator.py -v
```

**Cobertura actual**: 25 tests unitarios pasando ✅

## 📝 Notas de Desarrollo

- El archivo `.env` debe crearse manualmente copiando `.env.example`
- La limpieza automática se ejecuta cada hora (configurable en `scheduler.py`)
- Rate limiting: 60 requests por minuto por IP (configurable en `main.py`)
- Tamaño máximo de secreto: 10KB
- TTL: mínimo 5 minutos, máximo 7 días

## 🤝 Contribuciones

Este es un proyecto personal, pero las sugerencias son bienvenidas.

## 📄 Licencia

Proyecto privado - Autopus

## 👤 Autor

**Autopus**
- Web: https://autopus.es
- API: https://secret.autopus.es (próximamente)

---

**⚠️ Aviso**: Esta API está en desarrollo activo. No usar en producción hasta completar todos los pasos del roadmap.
