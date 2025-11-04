# Despliegue en Easypanel

Guía completa para desplegar Autopus Secret API en un servidor gestionado con Easypanel.

## 📋 Requisitos Previos

- Acceso a tu panel de Easypanel
- Repositorio Git accesible (GitHub, GitLab, etc.)
- Dominio `secret.autopus.es` apuntando a tu servidor (A record)
- Credenciales de Supabase (URL y API Key)

## 🚀 Método 1: Despliegue desde GitHub (Recomendado)

### Paso 1: Preparar el Repositorio

1. Asegúrate de que tu repositorio esté actualizado en GitHub/GitLab:
```bash
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### Paso 2: Crear Aplicación en Easypanel

1. Accede a tu panel de Easypanel
2. Navega a **Projects** → **New Project**
3. Nombre del proyecto: `autopus-secret-api`
4. Click en **Create**

### Paso 3: Añadir Servicio desde GitHub

1. Dentro del proyecto, click en **Add Service**
2. Selecciona **From Source** → **GitHub**
3. Autoriza Easypanel a acceder a tus repositorios si es necesario
4. Selecciona el repositorio `autopus-secret-api`
5. Branch: `main`
6. Build Method: **Dockerfile**

### Paso 4: Configurar Variables de Entorno

En la sección **Environment Variables**, añade:

```env
# Modo de ejecución
ENVIRONMENT=production

# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-publica-anon-key

# Security Keys (GENERAR NUEVOS PARA PRODUCCIÓN)
ENCRYPTION_KEY=nueva-clave-generada-con-fernet
API_KEY_ADMIN=clave-secreta-admin-segura

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=2
LOG_LEVEL=info

# Rate Limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
```

**⚠️ IMPORTANTE:** Genera nuevas claves de seguridad para producción:

```bash
# Generar ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generar API_KEY_ADMIN (64 caracteres hexadecimales)
python -c "import secrets; print(secrets.token_hex(32))"
```

### Paso 5: Configurar Dominio y SSL

1. En el servicio, ve a **Domains**
2. Click en **Add Domain**
3. Ingresa: `secret.autopus.es`
4. Easypanel automáticamente configurará SSL con Let's Encrypt
5. Espera 1-2 minutos para que el certificado SSL se emita

### Paso 6: Configurar Puertos

1. Ve a **Networking** en la configuración del servicio
2. Verifica que el puerto `8000` esté expuesto
3. Easypanel automáticamente configura el proxy inverso

### Paso 7: Desplegar

1. Click en **Deploy**
2. Easypanel construirá la imagen Docker usando tu Dockerfile
3. Espera 2-5 minutos para que el build complete
4. Verifica el estado en la pestaña **Logs**

### Paso 8: Verificar Despliegue

1. Abre tu navegador en `https://secret.autopus.es/health`
2. Deberías ver:
```json
{
  "status": "ok",
  "environment": "production",
  "timestamp": "2024-11-04T14:30:00+01:00"
}
```

3. Verifica Swagger UI: `https://secret.autopus.es/docs`

## 🐳 Método 2: Despliegue con Docker Compose

Si prefieres usar Docker Compose en Easypanel:

### Paso 1: Usar Template de Docker Compose

1. En Easypanel, crea un nuevo proyecto
2. Selecciona **Add Service** → **Docker Compose**
3. Usa el siguiente template:

```yaml
services:
  autopus-api:
    image: autopus-secret-api:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - API_KEY_ADMIN=${API_KEY_ADMIN}
      - HOST=0.0.0.0
      - PORT=8000
      - WORKERS=2
      - LOG_LEVEL=info
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    volumes:
      - ./logs:/app/logs
```

2. Configura las variables de entorno en el panel
3. Deploy

## 🔄 Actualización de la Aplicación

### Opción A: Auto-Deploy desde GitHub

1. En Easypanel, configura **Auto Deploy**:
   - Ve a la configuración del servicio
   - Activa **Auto Deploy on Push**
   - Easypanel desplegará automáticamente al hacer push a main

### Opción B: Deploy Manual

1. Haz push de tus cambios a GitHub:
```bash
git add .
git commit -m "Update: descripción de cambios"
git push origin main
```

2. En Easypanel, ve al servicio
3. Click en **Redeploy**
4. Easypanel reconstruirá y desplegará la nueva versión

### Opción C: Deploy desde Terminal

Si tienes SSH habilitado en Easypanel:

```bash
# Conectar por SSH a tu servidor
ssh usuario@tu-servidor

# Ir al directorio del proyecto
cd /app/autopus-secret-api

# Pull de cambios
git pull origin main

# Easypanel detectará cambios y reconstruirá automáticamente
# O fuerza un redeploy desde el panel
```

## 📊 Monitorización en Easypanel

### Ver Logs en Tiempo Real

1. Ve a tu servicio en Easypanel
2. Click en **Logs**
3. Verás los logs en tiempo real de tu aplicación

### Métricas del Servicio

1. En el dashboard del servicio verás:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

### Health Checks

Easypanel ejecuta automáticamente health checks basándose en tu Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## 🔧 Configuración Avanzada

### Escalar Workers

Para manejar más tráfico, puedes aumentar workers:

1. Modifica la variable de entorno `WORKERS`:
```env
WORKERS=4  # Aumentar a 4 workers
```

2. Redeploy el servicio

### Configurar Resource Limits

En Easypanel, puedes limitar recursos:

1. Ve a **Resources** en la configuración del servicio
2. Configura:
   - CPU: 0.5-1.0 cores
   - Memory: 512MB-1GB
   - Disk: según necesites

### Backup de Datos

**IMPORTANTE:** La base de datos está en Supabase, no en tu servidor de Easypanel.

Para backup de configuración:

1. Exporta variables de entorno regularmente
2. Mantén tu `.env` de producción en un lugar seguro (NO en Git)
3. Supabase hace backups automáticos de tu base de datos

## 🔒 Seguridad

### Variables de Entorno Sensibles

Easypanel encripta las variables de entorno automáticamente. Nunca expongas:

- `ENCRYPTION_KEY`
- `API_KEY_ADMIN`
- `SUPABASE_KEY` (aunque es pública, no la expongas innecesariamente)

### SSL/TLS

Easypanel gestiona automáticamente:
- Certificados Let's Encrypt
- Renovación automática cada 90 días
- Redirección HTTP → HTTPS

### Firewall

Easypanel configura automáticamente el firewall para:
- Puerto 80 (HTTP) - redirige a HTTPS
- Puerto 443 (HTTPS)
- Puerto 22 (SSH) - si está habilitado

## 🧪 Testing Post-Deployment

### 1. Health Check

```bash
curl https://secret.autopus.es/health
```

Respuesta esperada:
```json
{
  "status": "ok",
  "environment": "production",
  "timestamp": "2024-11-04T14:30:00+01:00"
}
```

### 2. Crear Secret de Prueba

```bash
curl -X POST https://secret.autopus.es/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Mensaje de prueba desde producción",
    "ttl_minutes": 60,
    "max_views": 1,
    "passphrase": "test123"
  }'
```

### 3. Verificar Admin Endpoints

```bash
curl https://secret.autopus.es/admin/system/info \
  -H "X-API-Key: tu-api-key-admin"
```

### 4. Verificar Swagger UI

Abre en navegador: `https://secret.autopus.es/docs`

## 🐛 Troubleshooting

### Problema: Build Falla

**Síntomas:** Error durante el build en Easypanel

**Solución:**
1. Verifica logs del build en Easypanel
2. Asegúrate que `requirements.txt` está actualizado
3. Verifica que el Dockerfile es correcto

### Problema: Aplicación No Inicia

**Síntomas:** Service en estado "Unhealthy" o "Crashed"

**Solución:**
1. Revisa logs en Easypanel → Logs
2. Verifica que todas las variables de entorno están configuradas
3. Verifica que `SUPABASE_URL` y `SUPABASE_KEY` son correctas
4. Asegúrate que el puerto 8000 está expuesto

### Problema: SSL No Funciona

**Síntomas:** Navegador muestra error de certificado

**Solución:**
1. Verifica que el dominio `secret.autopus.es` apunta correctamente a tu servidor
2. Espera 2-5 minutos para que Let's Encrypt emita el certificado
3. En Easypanel, ve a Domains y verifica el estado del SSL
4. Si persiste, elimina el dominio y vuelve a añadirlo

### Problema: 502 Bad Gateway

**Síntomas:** Nginx devuelve 502

**Solución:**
1. Verifica que la aplicación está corriendo: logs en Easypanel
2. Verifica que el puerto 8000 está escuchando
3. Revisa health check logs
4. Redeploy el servicio

### Problema: Rate Limit Muy Agresivo

**Síntomas:** Muchos requests bloqueados

**Solución:**
1. Ajusta variables de entorno:
```env
RATE_LIMIT_REQUESTS=120  # Aumentar a 120 requests
RATE_LIMIT_WINDOW=60     # por minuto
```
2. Redeploy

## 📈 Próximos Pasos

Una vez desplegado exitosamente:

1. **Monitorear Logs** durante las primeras 24 horas
2. **Configurar Alertas** en Easypanel para downtime
3. **Documentar tu API Key de Admin** en lugar seguro
4. **Crear Secrets de Prueba** para validar funcionalidad
5. **Configurar Backups** de variables de entorno

## 🔗 Enlaces Útiles

- **API en Producción:** https://secret.autopus.es
- **Swagger UI:** https://secret.autopus.es/docs
- **Health Check:** https://secret.autopus.es/health
- **Admin Info:** https://secret.autopus.es/admin/system/info

## 💡 Tips para Easypanel

1. **Auto Deploy:** Activa auto-deploy desde GitHub para despliegues automáticos
2. **Monitoring:** Usa el dashboard de Easypanel para monitorear uso de recursos
3. **Logs:** Revisa logs regularmente para detectar errores temprano
4. **Backups:** Exporta tu configuración de Easypanel regularmente
5. **Resources:** Ajusta CPU/Memory según el tráfico real de tu API

## ⚡ Quick Deploy Checklist

- [ ] Repositorio pushed a GitHub
- [ ] Proyecto creado en Easypanel
- [ ] Servicio configurado desde GitHub
- [ ] Variables de entorno añadidas (incluyendo claves nuevas)
- [ ] Dominio `secret.autopus.es` configurado
- [ ] SSL certificado emitido
- [ ] Deploy ejecutado
- [ ] Health check passing
- [ ] Swagger UI accesible
- [ ] Secret de prueba creado y verificado
- [ ] Admin endpoints probados
- [ ] Auto-deploy configurado (opcional)

---

**¡Listo para producción con Easypanel! 🎉**
