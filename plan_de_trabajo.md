# Plan de Trabajo - Autopus Secret API

## 📋 Resumen del Proyecto
API REST segura y autohosteada para compartir información sensible con acceso único y autodestrucción programada.

**Stack**: Python + FastAPI + Supabase + Cifrado AES-256

---

## 🗺️ Roadmap de Desarrollo

### **Paso 1: Estructura Inicial del Proyecto** ✅
**Objetivo**: Establecer la base del proyecto con la estructura de carpetas, dependencias y configuración inicial.

**Tareas**:
- [x] Crear estructura de carpetas del proyecto:
  ```
  autopus-secret-api/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py              # Punto de entrada de FastAPI
  │   ├── config.py            # Configuración y variables de entorno
  │   ├── routers/             # Endpoints organizados por módulo
  │   │   ├── __init__.py
  │   │   ├── secrets.py       # Endpoints públicos de secretos
  │   │   └── admin.py         # Endpoints administrativos
  │   ├── models/              # Modelos de datos (Pydantic)
  │   │   ├── __init__.py
  │   │   └── secret.py        # Modelo de secreto
  │   ├── services/            # Lógica de negocio
  │   │   ├── __init__.py
  │   │   ├── encryption.py    # Servicio de cifrado Fernet
  │   │   ├── database.py      # Cliente Supabase
  │   │   └── scheduler.py     # APScheduler para limpieza
  │   ├── schemas/             # Esquemas de validación
  │   │   ├── __init__.py
  │   │   └── secret.py        # DTOs de entrada/salida
  │   └── utils/               # Utilidades compartidas
  │       ├── __init__.py
  │       ├── token_generator.py
  │       └── validators.py
  ├── tests/                   # Tests unitarios y de integración
  ├── .env.example             # Plantilla de variables de entorno
  ├── .gitignore               # Archivos a ignorar en Git
  ├── requirements.txt         # Dependencias Python
  └── README.md                # Documentación del proyecto
  ```

- [x] Crear `requirements.txt` con dependencias:
  - `fastapi` - Framework web
  - `uvicorn[standard]` - Servidor ASGI
  - `supabase` - Cliente de Supabase
  - `cryptography` - Cifrado Fernet/AES-256
  - `bcrypt` - Hash de passphrases
  - `python-dotenv` - Gestión de variables de entorno
  - `apscheduler` - Tareas programadas
  - `pydantic` - Validación de datos
  - `pydantic-settings` - Configuración con Pydantic

- [x] Crear archivo `.env.example` con variables necesarias:
  - `SUPABASE_URL` - URL del proyecto Supabase
  - `SUPABASE_KEY` - API Key de Supabase
  - `ENCRYPTION_KEY` - Clave maestra para Fernet
  - `API_KEY_ADMIN` - API Key para endpoints administrativos
  - `ENVIRONMENT` - Entorno (development/production)
  - `CORS_ORIGINS` - Orígenes permitidos para CORS

- [x] Configurar FastAPI base en `app/main.py`:
  - Inicializar aplicación FastAPI
  - Configurar CORS
  - Incluir routers
  - Configurar documentación Swagger
  - Agregar middleware de seguridad

- [x] Crear archivo de configuración `app/config.py`:
  - Cargar variables de entorno
  - Validar configuración requerida
  - Exportar configuración centralizada

**Resultado esperado**: Proyecto con estructura profesional, listo para implementar la lógica de negocio. ✅

---

### **Paso 2: Configuración de Supabase** ✅
**Objetivo**: Diseñar e implementar el esquema de base de datos y configurar la conexión con Supabase.

**Tareas**:
- [x] Diseñar esquema de tabla `secrets` en Supabase:
  ```sql
  CREATE TABLE secrets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(64) UNIQUE NOT NULL,
    encrypted_content TEXT NOT NULL,
    passphrase_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accessed_at TIMESTAMP WITH TIME ZONE,
    is_destroyed BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'
  );
  ```

- [x] Crear índices para optimización:
  - Índice en `token` (búsqueda rápida)
  - Índice en `expires_at` (limpieza automática)
  - Índice en `is_destroyed` (filtrado de estado)

- [x] Configurar políticas RLS (Row Level Security) en Supabase:
  - Permitir INSERT público (crear secretos)
  - Permitir SELECT/UPDATE solo con token válido
  - Permitir DELETE con API Key admin
  - **Nota**: Por ahora se maneja a nivel de aplicación

- [x] Implementar cliente Supabase en `app/services/database.py`:
  - Inicializar cliente con credenciales
  - Métodos CRUD para secretos:
    - `create_secret()` - Insertar nuevo secreto ✅
    - `get_secret_by_token()` - Obtener por token ✅
    - `mark_as_accessed()` - Marcar como visto ✅
    - `delete_secret()` - Eliminar secreto ✅
    - `get_expired_secrets()` - Listar expirados ✅
    - `purge_expired()` - Eliminar expirados en lote ✅

- [x] Crear migraciones/scripts SQL para setup inicial

- [x] Probar conexión y operaciones básicas

**Resultado esperado**: Base de datos configurada y operativa con cliente Python funcional. ✅

---

### **Paso 3: Implementación del Core** ⏳
**Objetivo**: Desarrollar la funcionalidad principal de cifrado, modelos de datos y endpoints básicos.

**Tareas**:
- [ ] Implementar servicio de cifrado en `app/services/encryption.py`:
  - Generar/cargar clave Fernet desde variable de entorno
  - Método `encrypt(text: str) -> str` - Cifrar texto plano
  - Método `decrypt(encrypted: str) -> str` - Descifrar texto
  - Método `hash_passphrase(passphrase: str) -> str` - Hash bcrypt
  - Método `verify_passphrase(passphrase: str, hash: str) -> bool`
  - Manejo de excepciones de cifrado

- [ ] Crear generador de tokens en `app/utils/token_generator.py`:
  - Generar tokens únicos y seguros (64 caracteres)
  - Usar `secrets.token_urlsafe(48)` o similar
  - Validar unicidad contra base de datos

- [ ] Definir modelos Pydantic en `app/models/secret.py`:
  - `Secret` - Modelo de dominio completo
  - Campos: id, token, encrypted_content, expires_at, etc.

- [ ] Definir schemas de entrada/salida en `app/schemas/secret.py`:
  - `SecretCreateRequest` - DTO para crear secreto
    - content (str, requerido)
    - ttl_minutes (int, opcional, default 60)
    - passphrase (str, opcional)
  - `SecretCreateResponse` - Respuesta con URL/token
    - token (str)
    - url (str)
    - expires_at (datetime)
  - `SecretReadResponse` - Respuesta con contenido descifrado
    - content (str)
    - created_at (datetime)

- [ ] Implementar endpoints públicos en `app/routers/secrets.py`:
  - **POST /api/secret** - Crear secreto:
    1. Validar entrada (contenido, TTL)
    2. Generar token único
    3. Cifrar contenido
    4. Hash de passphrase (si existe)
    5. Calcular expires_at
    6. Guardar en Supabase
    7. Retornar token y URL
  
  - **GET /api/secret/{token}** - Obtener secreto:
    1. Buscar secreto por token
    2. Validar que no esté destruido
    3. Validar que no haya expirado
    4. Validar passphrase (si requerida)
    5. Descifrar contenido
    6. Marcar como destruido (accessed_at = NOW, is_destroyed = TRUE)
    7. Retornar contenido descifrado
  
  - **DELETE /api/secret/{token}/delete** - Destruir manualmente:
    1. Buscar secreto por token
    2. Marcar como destruido
    3. Retornar confirmación
  
  - **POST /api/secret/verify** - Validar passphrase:
    1. Recibir token + passphrase
    2. Verificar hash
    3. Retornar si es válida (sin revelar contenido)

- [ ] Implementar manejo de errores:
  - 404: Secreto no encontrado o ya destruido
  - 410: Secreto expirado
  - 401: Passphrase incorrecta
  - 400: Validación de entrada fallida

- [ ] Agregar logging básico (sin información sensible)

**Resultado esperado**: API funcional con capacidad de crear, leer y destruir secretos cifrados.

---

### **Paso 4: Funcionalidades Avanzadas** ⏳
**Objetivo**: Agregar tareas automáticas, endpoints administrativos y documentación completa.

**Tareas**:
- [ ] Implementar scheduler en `app/services/scheduler.py`:
  - Configurar APScheduler con BackgroundScheduler
  - Tarea: `cleanup_expired_secrets()` - Ejecutar cada hora
    1. Buscar secretos con `expires_at < NOW()`
    2. Eliminar de base de datos
    3. Registrar cantidad eliminada en logs
  - Iniciar scheduler al arrancar FastAPI
  - Detener scheduler al apagar aplicación

- [ ] Implementar middleware de autenticación admin:
  - Verificar header `Authorization: Bearer <API_KEY>`
  - Aplicar solo a rutas `/api/admin/*` o `/api/system/*`
  - Retornar 401 si falla autenticación

- [ ] Implementar endpoints administrativos en `app/routers/admin.py`:
  - **GET /api/stats** - Métricas globales:
    - Total secretos activos
    - Total secretos destruidos hoy
    - Total secretos expirados hoy
    - Promedio de tiempo hasta acceso
  
  - **DELETE /api/system/purge** - Forzar limpieza:
    - Ejecutar limpieza de expirados manualmente
    - Retornar cantidad eliminada
  
  - **GET /api/system/health** - Estado del sistema:
    - Verificar conexión a Supabase
    - Verificar estado del scheduler
    - Retornar status (healthy/unhealthy)
  
  - **GET /api/system/info** - Información del sistema:
    - Versión de la API
    - Uptime
    - Environment (dev/prod)
    - Última limpieza automática

- [ ] Configurar documentación OpenAPI/Swagger:
  - Personalizar título, descripción, versión
  - Agregar ejemplos de requests/responses
  - Documentar esquemas de autenticación
  - Agregar tags para agrupar endpoints (Public, Admin)

- [ ] Implementar validadores personalizados:
  - Validar rango de TTL (5 min - 7 días)
  - Validar longitud de contenido (máx 10KB)
  - Validar formato de passphrase (mín 6 caracteres)

- [ ] Agregar tests básicos:
  - Test de cifrado/descifrado
  - Test de creación de secreto
  - Test de acceso único (segunda lectura falla)
  - Test de expiración
  - Test de passphrase

- [ ] Crear README.md completo:
  - Descripción del proyecto
  - Requisitos previos
  - Instalación y configuración
  - Uso de la API (ejemplos con curl)
  - Despliegue en VPS
  - Variables de entorno
  - Arquitectura del sistema

- [ ] Preparar para despliegue:
  - Crear Dockerfile (opcional)
  - Configurar HTTPS con Caddy o Nginx
  - Script de inicio `start.sh`
  - Configurar logs persistentes

**Resultado esperado**: API completa, documentada y lista para producción con todas las funcionalidades del MVP.

---

## 📊 Estado del Proyecto

| Fase | Estado | Progreso |
|------|--------|----------|
| Paso 1: Estructura Inicial | ✅ Completado | 100% |
| Paso 2: Configuración Supabase | ✅ Completado | 100% |
| Paso 3: Implementación Core | ⏳ Pendiente | 0% |
| Paso 4: Funcionalidades Avanzadas | ⏳ Pendiente | 0% |

**Leyenda**: ⏳ Pendiente | 🔄 En Progreso | ✅ Completado

---

## 🎯 Próximos Pasos Inmediatos

1. ~~Revisar y aprobar este plan de trabajo~~ ✅
2. ~~Comenzar con **Paso 1**: Crear estructura de carpetas y archivos base~~ ✅
3. ~~Instalar dependencias: `pip install -r requirements.txt`~~ ✅
4. ~~Configurar variables de entorno: Copiar `.env.example` a `.env` y completar~~ ✅
5. ~~Comenzar con **Paso 2**: Configurar Supabase y crear esquema de base de datos~~ ✅
6. **Comenzar con Paso 3**: Implementar endpoints principales (crear y leer secretos)

---

## 📝 Notas
- Este documento se actualizará conforme avancemos en el desarrollo
- Cada tarea completada se marcará con ✅
- Se documentarán decisiones importantes y cambios de arquitectura
