# 📘 Guía Completa - Autopus Secret API

## 📋 Tabla de Contenidos

1. [Visión General del Sistema](#visión-general-del-sistema)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Estructura del Código](#estructura-del-código)
5. [API Endpoints](#api-endpoints)
6. [Seguridad y Cifrado](#seguridad-y-cifrado)
7. [Base de Datos (Supabase)](#base-de-datos-supabase)
8. [Deployment en Easypanel](#deployment-en-easypanel)
9. [Testing](#testing)
10. [Monitoreo y Logs](#monitoreo-y-logs)
11. [Troubleshooting](#troubleshooting)
12. [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Visión General del Sistema

### ¿Qué es Autopus Secret API?

**Autopus Secret API** es una API REST segura diseñada para compartir secretos (contraseñas, tokens, información sensible) de forma temporal y con autodestrucción automática. 

### Características Principales

✅ **Cifrado de extremo a extremo** con Fernet (AES-256)  
✅ **Autodestrucción** después de la primera lectura  
✅ **TTL (Time To Live)** configurable (5 minutos - 7 días)  
✅ **Protección con passphrase** opcional  
✅ **Límites de seguridad** (10KB máximo por secreto)  
✅ **Scheduler automático** para limpiar secretos expirados  
✅ **Admin endpoints** protegidos con API Key  
✅ **CSP (Content Security Policy)** configurado  
✅ **CORS** configurado para dominios específicos  
✅ **Health checks** para monitoreo  
✅ **Logs estructurados** con niveles configurables  

### Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Framework** | FastAPI | 0.115.0 |
| **Servidor ASGI** | Uvicorn | 0.32.0 |
| **Base de Datos** | Supabase (PostgreSQL) | 2.10.0 |
| **Cifrado** | Cryptography (Fernet) | 43.0.3 |
| **Hashing** | bcrypt | 4.2.1 |
| **Scheduler** | APScheduler | 3.10.4 |
| **Testing** | pytest + pytest-asyncio | 8.3.3 + 0.24.0 |
| **Validación** | Pydantic | 2.10.3 |
| **Deployment** | Docker + Easypanel | - |
| **Python** | 3.11-slim | 3.11 |

---

## 🏗️ Arquitectura del Proyecto

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                              │
│  (Browser, Postman, cURL, Frontend App)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    EASYPANEL (VPS)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              NGINX / Traefik                          │  │
│  │        (SSL, Load Balancing, Routing)                │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │          Docker Container (Python 3.11)              │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │           FastAPI Application                   │  │  │
│  │  │  ┌──────────────────────────────────────────┐  │  │  │
│  │  │  │  Routers (secrets, admin, health)        │  │  │  │
│  │  │  └──────────────┬───────────────────────────┘  │  │  │
│  │  │  ┌──────────────▼───────────────────────────┐  │  │  │
│  │  │  │  Middlewares (CORS, CSP, Security)       │  │  │  │
│  │  │  └──────────────┬───────────────────────────┘  │  │  │
│  │  │  ┌──────────────▼───────────────────────────┐  │  │  │
│  │  │  │  Services Layer                          │  │  │  │
│  │  │  │  - database_service                      │  │  │  │
│  │  │  │  - encryption_service                    │  │  │  │
│  │  │  └──────────────┬───────────────────────────┘  │  │  │
│  │  │  ┌──────────────▼───────────────────────────┐  │  │  │
│  │  │  │  Scheduler (APScheduler)                 │  │  │  │
│  │  │  │  - Cleanup job every hour                │  │  │  │
│  │  │  └──────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                     │                                 │  │
│  └─────────────────────┼─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SUPABASE (Cloud)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            PostgreSQL Database                        │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  Table: secrets                                 │  │  │
│  │  │  - id (uuid, PK)                                │  │  │
│  │  │  - token (text, unique)                         │  │  │
│  │  │  - encrypted_content (text)                     │  │  │
│  │  │  - passphrase_hash (text, nullable)             │  │  │
│  │  │  - expires_at (timestamptz)                     │  │  │
│  │  │  - accessed_at (timestamptz, nullable)          │  │  │
│  │  │  - is_destroyed (boolean)                       │  │  │
│  │  │  - metadata (jsonb)                             │  │  │
│  │  │  - created_at (timestamptz)                     │  │  │
│  │  │  - updated_at (timestamptz)                     │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos - Crear Secreto

```
Cliente → POST /api/secret
    ↓
Middleware (CORS, CSP)
    ↓
Router (secrets.py)
    ↓
Validación (Pydantic Schema)
    ↓
Generate Token (48 chars, URL-safe)
    ↓
Encrypt Content (Fernet AES-256)
    ↓
Hash Passphrase (bcrypt) [si existe]
    ↓
Database Service → Supabase
    ↓
Guardar en PostgreSQL
    ↓
Return Response (token, url, expires_at)
    ↓
Cliente ← 201 Created
```

### Flujo de Datos - Leer Secreto

```
Cliente → GET /api/secret/{token}
    ↓
Router (secrets.py)
    ↓
Database Service → Supabase
    ↓
Buscar por token
    ↓
¿Existe? ─NO→ 404 Not Found
    ↓ SÍ
¿Expirado? ─SÍ→ 404 Not Found
    ↓ NO
¿Destruido? ─SÍ→ 404 Not Found
    ↓ NO
¿Tiene passphrase? ─SÍ→ Pedir passphrase
    ↓ NO
Decrypt Content (Fernet)
    ↓
Marcar como destruido (is_destroyed=true)
    ↓
Return Response (content, created_at)
    ↓
Cliente ← 200 OK
```

---

## 🛠️ Instalación y Configuración

### Requisitos Previos

- **Python** 3.11+
- **Docker** (opcional, para deployment)
- **Git**
- **Cuenta Supabase** (gratis en supabase.com)
- **Servidor con Easypanel** (opcional, para deployment)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/RobertoRodriguezCarbonell/autopus-secret-api.git
cd autopus-secret-api
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copia el archivo `.env.example` (o crea `.env`):

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# ==================================================
# CONFIGURACIÓN DE SUPABASE
# ==================================================
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key_aqui

# ==================================================
# CIFRADO
# ==================================================
# Generar con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=tu_encryption_key_base64_aqui

# ==================================================
# AUTENTICACIÓN ADMIN
# ==================================================
# Generar con: python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEY_ADMIN=tu_api_key_admin_aqui

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================
ENVIRONMENT=development
# development | production

# ==================================================
# CORS - Orígenes permitidos (separados por comas)
# ==================================================
CORS_ORIGINS=http://localhost:3000,https://tu-dominio.com

# ==================================================
# CONFIGURACIÓN DE LA API
# ==================================================
API_HOST=0.0.0.0
API_PORT=8000
API_TITLE=Autopus Secret API
API_VERSION=0.1.0

# ==================================================
# LÍMITES Y SEGURIDAD
# ==================================================
MAX_SECRET_SIZE_KB=10
MIN_TTL_MINUTES=5
MAX_TTL_MINUTES=10080
# 10080 minutos = 7 días

# ==================================================
# SCHEDULER
# ==================================================
CLEANUP_INTERVAL_HOURS=1
```

### 5. Generar Claves de Seguridad

#### Encryption Key (Fernet)

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Ejemplo de salida:**
```
ofaxpnrkaPFGUzQPPisEsgUreADGLVCLoCy1AZAHuAE=
```

#### API Key Admin

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Ejemplo de salida:**
```
OO27m3vRoguPJ23wVMF4_Er7DpC7xh1y4ZxegF5V7Ds
```

### 6. Configurar Supabase

1. **Crear cuenta** en [supabase.com](https://supabase.com)
2. **Crear nuevo proyecto**
3. **Copiar credenciales**:
   - Project URL → `SUPABASE_URL`
   - Anon/Public Key → `SUPABASE_KEY`

4. **Crear tabla `secrets`** en SQL Editor:

```sql
-- Crear tabla secrets
CREATE TABLE secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token TEXT UNIQUE NOT NULL,
    encrypted_content TEXT NOT NULL,
    passphrase_hash TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    accessed_at TIMESTAMPTZ,
    is_destroyed BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear índices para mejorar rendimiento
CREATE INDEX idx_secrets_token ON secrets(token);
CREATE INDEX idx_secrets_expires_at ON secrets(expires_at);
CREATE INDEX idx_secrets_is_destroyed ON secrets(is_destroyed);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_secrets_updated_at 
    BEFORE UPDATE ON secrets 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Habilitar RLS (Row Level Security) - OPCIONAL
ALTER TABLE secrets ENABLE ROW LEVEL SECURITY;

-- Política: Permitir todas las operaciones (para desarrollo)
CREATE POLICY "Enable all operations for secrets" 
    ON secrets 
    FOR ALL 
    USING (true);

-- Para producción, considera políticas más restrictivas
```

### 7. Ejecutar Localmente

```bash
# Desarrollo (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Accede a:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📂 Estructura del Código

```
autopus-secret-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada, configuración FastAPI
│   ├── config.py                  # Configuración centralizada (Settings)
│   │
│   ├── routers/                   # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── secrets.py             # CRUD de secretos (público)
│   │   ├── admin.py               # Endpoints de administración
│   │   └── health.py              # Health check y status
│   │
│   ├── services/                  # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── database.py            # Interacción con Supabase
│   │   └── encryption.py          # Cifrado/descifrado (Fernet)
│   │
│   ├── middleware/                # Middlewares personalizados
│   │   ├── __init__.py
│   │   ├── security.py            # CSP, rate limiting
│   │   └── cors.py                # CORS configuration
│   │
│   ├── models/                    # Modelos de dominio
│   │   ├── __init__.py
│   │   └── secret.py              # Modelo Secret
│   │
│   ├── schemas/                   # DTOs (Pydantic)
│   │   ├── __init__.py
│   │   ├── secret.py              # Request/Response schemas
│   │   └── admin.py               # Admin schemas
│   │
│   ├── utils/                     # Utilidades
│   │   ├── __init__.py
│   │   ├── token_generator.py    # Generador de tokens únicos
│   │   └── validators.py         # Validaciones personalizadas
│   │
│   └── scheduler.py               # APScheduler jobs
│
├── tests/                         # Tests unitarios e integración
│   ├── __init__.py
│   ├── test_secrets.py            # Tests de secretos
│   ├── test_admin.py              # Tests de admin
│   ├── test_encryption.py         # Tests de cifrado
│   └── conftest.py                # Fixtures de pytest
│
├── .env                           # Variables de entorno (NO subir a Git)
├── .env.example                   # Plantilla de .env
├── .gitignore                     # Archivos ignorados por Git
├── .dockerignore                  # Archivos ignorados por Docker
├── Dockerfile                     # Configuración Docker
├── docker-compose.yml             # Compose (opcional, local)
├── requirements.txt               # Dependencias Python
├── pytest.ini                     # Configuración pytest
├── README.md                      # Documentación básica
├── EASYPANEL_DEPLOYMENT.md        # Guía de deployment
└── GUIA_COMPLETA.md              # Esta guía
```

### Descripción de Componentes Clave

#### `app/main.py`
- Inicialización de FastAPI
- Configuración de middlewares (CORS, CSP)
- Registro de routers
- Lifecycle events (startup/shutdown)
- Inicialización del scheduler

#### `app/config.py`
- Carga de variables de entorno con Pydantic Settings
- Validación de configuración
- Valores por defecto

#### `app/services/database.py`
- Singleton `DatabaseService`
- CRUD operations con Supabase
- Manejo de errores
- Logging estructurado

#### `app/services/encryption.py`
- Singleton `EncryptionService`
- Cifrado/descifrado con Fernet (AES-256)
- Hashing de passphrase con bcrypt
- Validación de passphrase

#### `app/scheduler.py`
- Configuración de APScheduler
- Job de limpieza cada hora
- Elimina secretos expirados y destruidos

---

## 🔌 API Endpoints

### Base URL

**Local:** `http://localhost:8000`  
**Producción:** `https://secret.autopus.es`

### Endpoints Públicos

#### 1. Root - Información de la API

```http
GET /
```

**Respuesta:**
```json
{
  "name": "Autopus Secret API",
  "version": "0.1.0",
  "status": "online",
  "docs": "/docs",
  "environment": "production"
}
```

---

#### 2. Health Check

```http
GET /health
```

**Respuesta:**
```json
{
  "status": "ok"
}
```

---

#### 3. Crear Secreto

```http
POST /api/secret
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "Mi mensaje secreto",
  "ttl_minutes": 60,
  "passphrase": "mi-password" // Opcional
}
```

**Parámetros:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `content` | string | ✅ | Contenido del secreto (máx 10KB) |
| `ttl_minutes` | integer | ❌ | Tiempo de vida (5-10080, default 60) |
| `passphrase` | string | ❌ | Contraseña de protección (mín 6 chars) |

**Respuesta (201 Created):**
```json
{
  "token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234",
  "url": "https://secret.autopus.es/api/secret/abc123def456ghi789jkl012mno345pqr678stu901vwx234",
  "expires_at": "2025-11-04T17:00:00Z",
  "has_passphrase": false
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 400 | Validación fallida (contenido muy grande, TTL inválido) |
| 500 | Error interno del servidor |

---

#### 4. Leer Secreto (Sin Passphrase)

```http
GET /api/secret/{token}
```

**Parámetros de Ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `token` | string | Token único del secreto |

**Respuesta (200 OK):**
```json
{
  "content": "Mi mensaje secreto",
  "created_at": "2025-11-04T16:00:00Z",
  "message": "Este secreto ha sido destruido y no puede volver a ser accedido"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 404 | Secreto no encontrado, expirado o ya consumido |
| 403 | Secreto protegido con passphrase (usar /api/secret/verify) |

---

#### 5. Verificar Passphrase y Leer Secreto

```http
POST /api/secret/verify
Content-Type: application/json
```

**Request Body:**
```json
{
  "token": "abc123...",
  "passphrase": "mi-password"
}
```

**Respuesta (200 OK):**
```json
{
  "content": "Mi mensaje secreto protegido",
  "created_at": "2025-11-04T16:00:00Z",
  "message": "Este secreto ha sido destruido y no puede volver a ser accedido"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 401 | Passphrase incorrecta |
| 404 | Secreto no encontrado o expirado |

---

### Endpoints de Administración

**⚠️ Requieren autenticación con `X-API-Key` header**

#### 6. Listar Todos los Secretos

```http
GET /api/admin/secrets
X-API-Key: tu_api_key_admin
```

**Respuesta (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "token": "abc123...",
    "has_passphrase": false,
    "expires_at": "2025-11-04T17:00:00Z",
    "accessed_at": null,
    "is_destroyed": false,
    "created_at": "2025-11-04T16:00:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "token": "xyz789...",
    "has_passphrase": true,
    "expires_at": "2025-11-05T10:00:00Z",
    "accessed_at": "2025-11-04T16:30:00Z",
    "is_destroyed": true,
    "created_at": "2025-11-04T15:00:00Z"
  }
]
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 401 | API Key faltante o inválida |

---

#### 7. Obtener Estadísticas

```http
GET /api/admin/stats
X-API-Key: tu_api_key_admin
```

**Respuesta (200 OK):**
```json
{
  "total_secrets": 150,
  "active_secrets": 45,
  "expired_secrets": 30,
  "consumed_secrets": 75
}
```

**Definiciones:**
- `total_secrets`: Total de secretos en BD
- `active_secrets`: No destruidos y no expirados
- `expired_secrets`: Expirados pero no destruidos
- `consumed_secrets`: Marcados como destruidos

---

#### 8. Eliminar Secreto Específico

```http
DELETE /api/admin/secrets/{secret_id}
X-API-Key: tu_api_key_admin
```

**Parámetros de Ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `secret_id` | uuid | ID del secreto |

**Respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Secreto eliminado correctamente"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 401 | API Key faltante o inválida |
| 404 | Secreto no encontrado |

---

#### 9. Forzar Limpieza de Secretos Expirados

```http
POST /api/admin/cleanup
X-API-Key: tu_api_key_admin
```

**Respuesta (200 OK):**
```json
{
  "deleted_count": 15,
  "message": "Limpieza completada exitosamente"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 401 | API Key faltante o inválida |

---

## 🔐 Seguridad y Cifrado

### Cifrado (Fernet - AES-256)

**Autopus Secret API** utiliza **Fernet** de la librería `cryptography` para cifrado simétrico:

- **Algoritmo:** AES-256-CBC
- **Autenticación:** HMAC-SHA256
- **Generación de claves:** URL-safe base64

#### Cómo funciona:

1. **Generar clave:**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()  # 32 bytes, base64-encoded
```

2. **Cifrar:**
```python
cipher = Fernet(key)
encrypted = cipher.encrypt(plaintext.encode())
```

3. **Descifrar:**
```python
decrypted = cipher.decrypt(encrypted).decode()
```

### Hashing de Passphrase (bcrypt)

Para proteger secretos con contraseña, se usa **bcrypt**:

- **Algoritmo:** bcrypt (Blowfish adaptativo)
- **Cost factor:** 12 rounds (configurable)
- **Salt:** Generado automáticamente

#### Cómo funciona:

1. **Hash:**
```python
import bcrypt
hashed = bcrypt.hashpw(passphrase.encode(), bcrypt.gensalt(rounds=12))
```

2. **Verificar:**
```python
is_valid = bcrypt.checkpw(passphrase.encode(), hashed)
```

### Generación de Tokens

Los tokens son **URL-safe, criptográficamente seguros**:

- **Longitud:** 48 caracteres
- **Alfabeto:** `A-Za-z0-9_-`
- **Entropía:** ~288 bits
- **Colisiones:** Prácticamente imposibles

```python
import secrets
token = secrets.token_urlsafe(36)  # 48 chars después de encoding
```

### Content Security Policy (CSP)

Headers CSP aplicados automáticamente:

```http
Content-Security-Policy: 
  default-src 'self'; 
  script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; 
  style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; 
  img-src 'self' data: https:; 
  font-src 'self' https://cdn.jsdelivr.net; 
  connect-src 'self';
```

### CORS (Cross-Origin Resource Sharing)

Configurado para dominios específicos:

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://secret.autopus.es"
]
```

### Rate Limiting (Recomendado para Producción)

⚠️ **Pendiente de implementar** - Se recomienda usar:
- Cloudflare (5 req/s por IP)
- Nginx limit_req
- FastAPI middleware custom

---

## 💾 Base de Datos (Supabase)

### Schema de la Tabla `secrets`

```sql
CREATE TABLE secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token TEXT UNIQUE NOT NULL,
    encrypted_content TEXT NOT NULL,
    passphrase_hash TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    accessed_at TIMESTAMPTZ,
    is_destroyed BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Campos Explicados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único (auto-generado) |
| `token` | TEXT | Token URL-safe único (48 chars) |
| `encrypted_content` | TEXT | Contenido cifrado con Fernet |
| `passphrase_hash` | TEXT | Hash bcrypt de la passphrase (nullable) |
| `expires_at` | TIMESTAMPTZ | Fecha/hora de expiración (UTC) |
| `accessed_at` | TIMESTAMPTZ | Primera lectura (nullable) |
| `is_destroyed` | BOOLEAN | Marca de autodestrucción |
| `metadata` | JSONB | Datos adicionales (IP, user-agent, etc.) |
| `created_at` | TIMESTAMPTZ | Fecha de creación |
| `updated_at` | TIMESTAMPTZ | Última modificación (auto-update) |

### Índices

```sql
CREATE INDEX idx_secrets_token ON secrets(token);
CREATE INDEX idx_secrets_expires_at ON secrets(expires_at);
CREATE INDEX idx_secrets_is_destroyed ON secrets(is_destroyed);
```

**Propósito:**
- Búsquedas rápidas por token
- Optimizar queries de limpieza (expirados)
- Filtrar por estado de destrucción

### Row Level Security (RLS)

⚠️ **Opcional pero recomendado para producción**

```sql
ALTER TABLE secrets ENABLE ROW LEVEL SECURITY;

-- Política permisiva (desarrollo)
CREATE POLICY "Enable all operations for secrets" 
    ON secrets 
    FOR ALL 
    USING (true);

-- Política restrictiva (producción - ejemplo)
CREATE POLICY "Users can only read their own secrets" 
    ON secrets 
    FOR SELECT 
    USING (metadata->>'user_id' = auth.uid()::text);
```

### Queries Comunes

#### Obtener secreto por token
```sql
SELECT * FROM secrets 
WHERE token = 'abc123...' 
  AND is_destroyed = FALSE 
  AND expires_at > NOW();
```

#### Limpiar expirados
```sql
DELETE FROM secrets 
WHERE expires_at < NOW() 
   OR is_destroyed = TRUE;
```

#### Estadísticas
```sql
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE NOT is_destroyed AND expires_at > NOW()) as active,
    COUNT(*) FILTER (WHERE expires_at < NOW()) as expired,
    COUNT(*) FILTER (WHERE is_destroyed) as consumed
FROM secrets;
```

---

## 🚀 Deployment en Easypanel

### Requisitos

- Servidor VPS con Easypanel instalado
- Dominio apuntando al servidor (A record)
- Repositorio GitHub configurado

### Paso 1: Crear Proyecto en Easypanel

1. Login en Easypanel
2. **Projects** → **Create Project**
3. Nombre: `autopus-secret-api`

### Paso 2: Crear App Service

1. Dentro del proyecto → **Create Service**
2. Tipo: **App**
3. Nombre: `autopus-secret-api`

### Paso 3: Configurar Source

1. **Source:** GitHub
2. **Repository:** `RobertoRodriguezCarbonell/autopus-secret-api`
3. **Branch:** `main`
4. **Autenticación:** GitHub App o Personal Access Token

### Paso 4: Configurar Build

1. **Build Method:** `Dockerfile`
2. **Dockerfile Path:** `Dockerfile`
3. **Build Context:** `.` (root)

### Paso 5: Configurar Network

1. **Internal Port:** `8000`
2. **Domain:** `secret.autopus.es`
3. **Enable SSL:** ✅ (Let's Encrypt automático)

### Paso 6: Variables de Entorno

Añadir en **Environment Variables**:

```env
SUPABASE_URL=https://zzbovjgqxcntysuwcxzm.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ENCRYPTION_KEY=ofaxpnrkaPFGUzQPPisEsgUreADGLVCLoCy1AZAHuAE=
API_KEY_ADMIN=OO27m3vRoguPJ23wVMF4_Er7DpC7xh1y4ZxegF5V7Ds
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
WORKERS=2
```

### Paso 7: Deploy

1. Click en **Save** o **Deploy**
2. Esperar build (2-3 minutos)
3. Verificar logs

### Verificación Post-Deploy

```bash
# Health check
curl https://secret.autopus.es/health

# API info
curl https://secret.autopus.es/

# Docs
open https://secret.autopus.es/docs
```

### Actualizar Deployment

```bash
# 1. Hacer cambios en código
# 2. Commit y push
git add .
git commit -m "Update feature X"
git push origin main

# 3. En Easypanel, el webhook disparará auto-deploy
# O manualmente: Click en "Rebuild"
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_secrets.py
pytest tests/test_admin.py -v

# Modo verbose
pytest -vv
```

### Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidas
├── test_secrets.py          # Tests de secretos
├── test_admin.py            # Tests de admin
├── test_encryption.py       # Tests de cifrado
└── test_database.py         # Tests de BD
```

### Ejemplo de Test

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_secret():
    response = client.post("/api/secret", json={
        "content": "Test secret",
        "ttl_minutes": 60
    })
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert len(data["token"]) == 48

def test_read_secret():
    # Create
    create_response = client.post("/api/secret", json={
        "content": "Test secret"
    })
    token = create_response.json()["token"]
    
    # Read
    read_response = client.get(f"/api/secret/{token}")
    assert read_response.status_code == 200
    assert read_response.json()["content"] == "Test secret"
    
    # Try read again (should fail - auto-destroyed)
    read_again = client.get(f"/api/secret/{token}")
    assert read_again.status_code == 404
```

### Coverage Report

Después de ejecutar `pytest --cov=app`, abre `htmlcov/index.html` para ver reporte detallado.

**Objetivo:** ≥80% de cobertura

---

## 📊 Monitoreo y Logs

### Logs Estructurados

La aplicación genera logs con niveles:

```python
import logging

logger = logging.getLogger(__name__)

# Niveles:
logger.debug("Detalle técnico")      # DEBUG
logger.info("Operación normal")      # INFO
logger.warning("Advertencia")        # WARNING
logger.error("Error recuperable")    # ERROR
logger.critical("Error crítico")     # CRITICAL
```

### Ver Logs en Easypanel

1. Ir al servicio `autopus-secret-api`
2. Pestaña **Logs**
3. Filtrar por nivel o búsqueda

### Logs Importantes

#### Startup
```
INFO - 🚀 Iniciando Autopus Secret API...
INFO - 📍 Entorno: production
INFO - 🔒 Cifrado: Habilitado
INFO - ⏰ Scheduler iniciado correctamente
```

#### Operaciones
```
INFO - Token generado para nuevo secreto: abc123...
INFO - ✅ Secreto guardado en BD: abc123...
INFO - 📖 Secreto leído y destruido: abc123...
```

#### Errores
```
ERROR - ❌ Error al obtener secreto: {'message': 'Invalid API key'}
ERROR - Error al crear secreto: Validation failed
```

### Health Checks

Easypanel hace health checks automáticos cada 30 segundos:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Métricas Recomendadas (Para Implementar)

- **Request rate** (req/s)
- **Error rate** (%)
- **Response time** (p50, p95, p99)
- **Database query time**
- **Active secrets count**
- **Cleanup job duration**

**Herramientas sugeridas:**
- Prometheus + Grafana
- New Relic
- Datadog
- Sentry (errores)

---

## 🔧 Troubleshooting

### Problema: "Not Found" al llamar endpoint

**Síntomas:**
```json
{"detail": "Not Found"}
```

**Causas:**
1. URL incorrecta (falta `/api` prefix)
2. Método HTTP incorrecto (GET vs POST)
3. Router no registrado

**Solución:**
```bash
# ❌ Incorrecto
POST https://secret.autopus.es/secret

# ✅ Correcto
POST https://secret.autopus.es/api/secret
```

---

### Problema: "Invalid API key" en Supabase

**Síntomas:**
```
ERROR - ❌ Error al obtener secreto: {'message': 'Invalid API key'}
```

**Causas:**
1. `SUPABASE_KEY` incorrecta en variables de entorno
2. Usando service_role key en lugar de anon key
3. Proyecto Supabase pausado/eliminado

**Solución:**
1. Verificar key en Supabase Dashboard
2. Actualizar en Easypanel Environment Variables
3. Redeploy

---

### Problema: Secreto no se destruye después de leer

**Síntomas:**
- Puedes leer el secreto múltiples veces

**Causas:**
1. Flag `is_destroyed` no se actualiza
2. Error en lógica de destrucción

**Solución:**
Verificar en código:
```python
await database_service.mark_as_destroyed(token)
```

---

### Problema: Scheduler no limpia secretos expirados

**Síntomas:**
- Base de datos crece indefinidamente
- Secretos expirados no se eliminan

**Causas:**
1. Scheduler no iniciado
2. Job mal configurado
3. Error en función de limpieza

**Solución:**
1. Verificar logs de startup:
```
INFO - ⏰ Scheduler iniciado correctamente
INFO - 📅 Job 'cleanup_expired_secrets' programado cada hora
```

2. Forzar limpieza manual:
```bash
curl -X POST https://secret.autopus.es/api/admin/cleanup \
  -H "X-API-Key: tu_api_key"
```

---

### Problema: Docker build falla en Easypanel

**Síntomas:**
```
ERROR: failed to solve: process "/bin/sh -c pip install" did not complete
```

**Causas:**
1. requirements.txt con dependencias conflictivas
2. Dockerfile mal configurado
3. Build context vacío

**Solución:**
1. Verificar requirements.txt (sin duplicados)
2. Probar build local:
```bash
docker build -t autopus-test .
docker run -p 8000:8000 autopus-test
```

---

### Problema: CORS errors en frontend

**Síntomas:**
```
Access to fetch at 'https://secret.autopus.es/api/secret' 
from origin 'https://mi-frontend.com' has been blocked by CORS policy
```

**Solución:**
Añadir origen en `.env`:
```env
CORS_ORIGINS=http://localhost:3000,https://mi-frontend.com,https://secret.autopus.es
```

Redeploy.

---

## ✅ Mejores Prácticas

### Seguridad

1. **Nunca commitear `.env`** en Git
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Rotar claves periódicamente**
   - ENCRYPTION_KEY cada 6 meses
   - API_KEY_ADMIN cada 3 meses

3. **Usar HTTPS siempre** en producción

4. **Implementar rate limiting** en producción

5. **Monitorear logs** para detectar ataques

### Desarrollo

1. **Usar entorno virtual** siempre
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Ejecutar tests antes de deploy**
   ```bash
   pytest && git push
   ```

3. **Mantener dependencias actualizadas**
   ```bash
   pip list --outdated
   pip install -U nombre-paquete
   ```

4. **Usar pre-commit hooks** (opcional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Deployment

1. **Variables de entorno separadas** por ambiente
   - `.env.development`
   - `.env.production`

2. **Automatizar deployment** con CI/CD
   - GitHub Actions
   - GitLab CI
   - Easypanel webhooks

3. **Backup de base de datos** regularmente
   - Supabase hace backups automáticos (Pro plan)
   - Exportar manualmente si es gratis

4. **Monitorear uptime**
   - UptimeRobot
   - Pingdom
   - StatusCake

### Base de Datos

1. **Crear índices** en campos de búsqueda frecuente

2. **Limpiar datos** periódicamente
   - Scheduler automático cada hora
   - Limpieza manual mensual

3. **Usar transacciones** para operaciones críticas

4. **Validar datos** en múltiples capas:
   - Pydantic schemas
   - Database constraints
   - Business logic

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Supabase Docs](https://supabase.com/docs)
- [Cryptography Docs](https://cryptography.io/)
- [APScheduler Docs](https://apscheduler.readthedocs.io/)
- [Pydantic Docs](https://docs.pydantic.dev/)

### Tutoriales

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Docker for Python](https://docker-curriculum.com/#docker-for-python-developers)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

### Comunidad

- [FastAPI Discord](https://discord.com/invite/VQjSZaeJmf)
- [Supabase Discord](https://discord.supabase.com/)
- [Python Discord](https://discord.gg/python)

---

## 📞 Soporte

### Contacto

- **Email:** info@autopus.es
- **GitHub:** [RobertoRodriguezCarbonell/autopus-secret-api](https://github.com/RobertoRodriguezCarbonell/autopus-secret-api)
- **Issues:** [GitHub Issues](https://github.com/RobertoRodriguezCarbonell/autopus-secret-api/issues)

### Reportar Bugs

1. Abrir issue en GitHub
2. Incluir:
   - Descripción del problema
   - Pasos para reproducir
   - Logs relevantes
   - Versión de Python/dependencias

### Contribuir

1. Fork del repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m "Add nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request

---

## 📄 Licencia

**MIT License**

Copyright (c) 2025 Autopus

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🎉 Conclusión

¡Felicidades! Ahora tienes una **guía completa** de Autopus Secret API. Este documento cubre:

✅ Instalación y configuración  
✅ Arquitectura y estructura  
✅ Todos los endpoints de la API  
✅ Seguridad y cifrado  
✅ Base de datos  
✅ Deployment en Easypanel  
✅ Testing  
✅ Monitoreo y logs  
✅ Troubleshooting  
✅ Mejores prácticas  

**Siguiente paso:** Implementa mejoras como rate limiting, métricas avanzadas o un frontend para compartir secretos de forma visual.

---

**Versión:** 1.0.0  
**Fecha:** 4 de noviembre de 2025  
**Autor:** Roberto Rodríguez Carbonell (@Autopus)
