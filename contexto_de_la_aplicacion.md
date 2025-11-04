Contexto general del proyecto:
Estoy desarrollando Autopus Secret API, un servicio privado y autohosteado para compartir contraseñas, claves API o información sensible entre equipos o clientes, sin depender de terceros ni dejar trazas persistentes.
Quiero construirlo con Python + FastAPI + Supabase, con énfasis en seguridad, simplicidad, control total y futuras integraciones con automatizaciones como n8n.

Objetivo principal:
Crear una API Rest segura, privada y auto-gestionada que permita generar, consultar y destruir secretos cifrados con caducidad configurable, accesibles solo una vez mediante un enlace único.

Stack técnico:
Lenguaje: Python
Framework: FastAPI
Base de datos: Supabase
Cliente DB: supabase-py
Cifrado: cryptography (AES-256 / Fernet) + bcrypt (para passphrases)
Tareas automáticas: APScheduler (limpieza de secretos expirados)
Infraestructura: VPS propio (Hostinger/Easypanel) bajo dominio secret.autopus.es con HTTPS
Autenticación admin: API Key (Authorization: Bearer <clave>)
Integraciones externas: n8n, Postman y futuros frontends

Principios de diseño:
One-Time Access: Cada secreto solo puede visualizarse una vez; después se marca como destruido.
Expiración programada: Tiempo de vida configurable (5 min - 7 días). Eliminación automática al expirar.
Cifrado fuerte: Los datos se cifran antes de guardarse; Supabase nunca almacena texto plano.
Anonimato opcional: Uso sin autenticación; soporte futuro para usuarios autenticados de Supabase.
Trazabilidad mínima: Solo se registran metadatos (token, fecha, expiración, estado).

Funcionalidades (MVP):
Crear secreto con texto, caducidad y passphrase opcional.
Generar token único (URL).
Leer secreto una sola vez y marcarlo como "visto".
Auto-borrado al expirar.
Endpoints públicos accesibles desde Postman o n8n.
Endpoints administrativos protegidos por API Key.

Funcionalidades (v2 - plan futuro):
Notificaciones (email, slack, telegram) al visualizar el secreto.
Destrucción manual previa a lectura.
Estadísticas internas (activos, expirados, vistos).
Autenticación Supabase multiusuario.
API pública documentada (OpenAPI/Swagger).
Autodestrucción inmediata tras lectura.

Endpoints principales:
Público -> /api/secret -> POST -> Crear secreto cifrado -> Autenticación: no
Público -> /api/secret/{token} -> GET -> Obtener y destruir secreto -> Autenticación: no
Público -> /api/secret/{token}/delete -> DELETE -> Destruir secreto manualmente -> Autenticación: no
Público -> /api/secret/verify -> POST -> Validar passphrase -> Autenticación: no
Privado -> /api/stats -> GET -> Métricas globales -> Autenticación: API Key
Privado -> /api/system/purge -> DELETE -> Eliminar expirados -> Autenticación: API Key
Privado -> /api/system/health -> GET -> Estado del sistema -> Autenticación: API Key
Privado -> /api/system/info -> GET -> Info de versión/uptime -> Autenticación: API Key

Seguridad:
Cifrado Fernet (AES-256) antes de guardar en Supabase.
Tokens aleatorios (secrets.token_urlsafe() o nanoid).
API Key para endpoints administrativos.
Conexión HTTPS obligatoria.
Limpieza automática de datos expirados cada hora (APScheduler).
Sin almacenamiento de texto plano ni logs sensibles.
Rate Limiting: 60 requests por minuto por IP.
Security Headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS, etc.

Contexto de negocio:
El proyecto forma parte de mi ecosistema Autopus, centrado en la automatización y herramientas seguras.
Esta API servirá tanto como herramienta interna como base para un microservicio SaaS a medio plazo.
Debe ser estable, auditada y fácilmente integrable.

Estado actual (v1.0.0 Beta):
✅ Paso 1: Estructura inicial completada
✅ Paso 2: Configuración Supabase completada
✅ Paso 3: Core implementation completada
✅ Paso 4: Funcionalidades avanzadas completadas
  - APScheduler con limpieza automática cada hora
  - Endpoints administrativos (/admin/stats, /admin/system/*)
  - Security Middleware (RateLimitMiddleware, SecurityHeadersMiddleware)
  - Tests unitarios (25/25 pasando con pytest)
  - Documentación completa con ejemplos y deployment

La API está completamente funcional y lista para producción (beta).