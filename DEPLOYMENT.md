# 🚀 Guía de Deployment - Autopus Secret API

## Deployment en VPS para secret.autopus.es

Esta guía te llevará paso a paso para desplegar la API en tu VPS con dominio personalizado.

---

## 📋 Prerequisitos

- ✅ VPS con Ubuntu 20.04+ o similar
- ✅ Dominio `secret.autopus.es` configurado apuntando a tu VPS
- ✅ Acceso SSH root o sudo
- ✅ Cuenta de Supabase configurada

---

## 🔧 Paso 1: Preparar el VPS

### 1.1 Conectar al VPS

```bash
ssh root@tu-ip-del-vps
# o
ssh usuario@tu-ip-del-vps
```

### 1.2 Actualizar el sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Instalar dependencias necesarias

```bash
# Python 3.11+
sudo apt install -y python3 python3-pip python3-venv

# Nginx (reverse proxy)
sudo apt install -y nginx

# Certbot (SSL/HTTPS)
sudo apt install -y certbot python3-certbot-nginx

# Git
sudo apt install -y git

# Supervisor (gestión de procesos)
sudo apt install -y supervisor
```

### 1.4 Verificar instalaciones

```bash
python3 --version  # Debe ser 3.9+
nginx -v
certbot --version
```

---

## 📦 Paso 2: Clonar el proyecto

### 2.1 Crear usuario para la aplicación (recomendado)

```bash
sudo adduser autopus --disabled-password --gecos ""
sudo usermod -aG sudo autopus
```

### 2.2 Cambiar al usuario

```bash
sudo su - autopus
```

### 2.3 Clonar repositorio

```bash
cd ~
git clone https://github.com/RobertoRodriguezCarbonell/autopus-secret-api.git
cd autopus-secret-api
```

> **Nota**: Si tu repo es privado, necesitarás configurar SSH keys o usar personal access token

### 2.4 Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.5 Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔐 Paso 3: Configurar variables de entorno

### 3.1 Crear archivo .env

```bash
nano .env
```

### 3.2 Contenido del .env (PRODUCCIÓN)

```properties
# ==================================================
# CONFIGURACIÓN DE SUPABASE
# ==================================================
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anon-key-aqui

# ==================================================
# CIFRADO
# ==================================================
ENCRYPTION_KEY=tu-clave-de-cifrado-fernet

# ==================================================
# AUTENTICACIÓN ADMIN
# ==================================================
API_KEY_ADMIN=tu-api-key-admin-segura

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================
ENVIRONMENT=production

# ==================================================
# CORS - Orígenes permitidos
# ==================================================
CORS_ORIGINS=https://secret.autopus.es

# ==================================================
# CONFIGURACIÓN DE LA API
# ==================================================
API_HOST=127.0.0.1
API_PORT=8000
API_TITLE=Autopus Secret API
API_VERSION=1.0.0

# ==================================================
# LÍMITES Y SEGURIDAD
# ==================================================
MAX_SECRET_SIZE_KB=10
MIN_TTL_MINUTES=5
MAX_TTL_MINUTES=10080

# ==================================================
# SCHEDULER
# ==================================================
CLEANUP_INTERVAL_HOURS=1
```

### 3.3 Proteger el archivo

```bash
chmod 600 .env
```

### 3.4 Generar claves necesarias (si no las tienes)

```bash
# Generar ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generar API_KEY_ADMIN
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔄 Paso 4: Configurar Supervisor (mantener API corriendo)

### 4.1 Crear archivo de configuración

```bash
sudo nano /etc/supervisor/conf.d/autopus-secret.conf
```

### 4.2 Contenido del archivo

```ini
[program:autopus-secret-api]
directory=/home/autopus/autopus-secret-api
command=/home/autopus/autopus-secret-api/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
user=autopus
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/autopus-secret/error.log
stdout_logfile=/var/log/autopus-secret/access.log
environment=PATH="/home/autopus/autopus-secret-api/venv/bin"
```

### 4.3 Crear directorio de logs

```bash
sudo mkdir -p /var/log/autopus-secret
sudo chown autopus:autopus /var/log/autopus-secret
```

### 4.4 Recargar y activar Supervisor

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start autopus-secret-api
```

### 4.5 Verificar estado

```bash
sudo supervisorctl status autopus-secret-api
```

Deberías ver: `autopus-secret-api RUNNING`

---

## 🌐 Paso 5: Configurar Nginx (Reverse Proxy)

### 5.1 Crear archivo de configuración

```bash
sudo nano /etc/nginx/sites-available/secret.autopus.es
```

### 5.2 Contenido del archivo (HTTP - temporal)

```nginx
server {
    listen 80;
    server_name secret.autopus.es;

    # Logs
    access_log /var/log/nginx/secret-autopus-access.log;
    error_log /var/log/nginx/secret-autopus-error.log;

    # Tamaño máximo de request body
    client_max_body_size 1M;

    # Proxy a la aplicación
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

### 5.3 Activar el sitio

```bash
sudo ln -s /etc/nginx/sites-available/secret.autopus.es /etc/nginx/sites-enabled/
```

### 5.4 Verificar configuración

```bash
sudo nginx -t
```

### 5.5 Recargar Nginx

```bash
sudo systemctl reload nginx
```

### 5.6 Verificar que Nginx esté corriendo

```bash
sudo systemctl status nginx
```

---

## 🔒 Paso 6: Configurar SSL/HTTPS con Let's Encrypt

### 6.1 Asegurar que el dominio apunta al VPS

Verifica en tu DNS que `secret.autopus.es` tenga un registro A apuntando a la IP de tu VPS:

```bash
dig secret.autopus.es +short
# Debe mostrar tu IP del VPS
```

### 6.2 Obtener certificado SSL

```bash
sudo certbot --nginx -d secret.autopus.es
```

Sigue las instrucciones:
1. Ingresa tu email
2. Acepta términos de servicio
3. Elige si compartir email (opcional)
4. Elige opción 2: "Redirect HTTP to HTTPS" (recomendado)

### 6.3 Verificar renovación automática

```bash
sudo certbot renew --dry-run
```

### 6.4 Configuración final de Nginx (actualizada por Certbot)

Certbot habrá modificado automáticamente el archivo. Verifica:

```bash
sudo nano /etc/nginx/sites-available/secret.autopus.es
```

Debería incluir algo como:

```nginx
server {
    server_name secret.autopus.es;

    # ... resto de configuración ...

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/secret.autopus.es/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/secret.autopus.es/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = secret.autopus.es) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name secret.autopus.es;
    return 404;
}
```

---

## ✅ Paso 7: Verificar deployment

### 7.1 Probar desde navegador

Visita: `https://secret.autopus.es`

Deberías ver:
```json
{
  "name": "Autopus Secret API",
  "version": "1.0.0",
  "status": "online",
  "docs": "/docs",
  "environment": "production"
}
```

### 7.2 Probar documentación

Visita: `https://secret.autopus.es/docs`

### 7.3 Probar health check

```bash
curl https://secret.autopus.es/health
```

### 7.4 Probar creación de secreto

```bash
curl -X POST "https://secret.autopus.es/api/secret" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test secreto",
    "ttl_minutes": 60
  }'
```

---

## 🔧 Comandos útiles de administración

### Reiniciar la aplicación

```bash
sudo supervisorctl restart autopus-secret-api
```

### Ver logs en tiempo real

```bash
# Logs de la aplicación
sudo tail -f /var/log/autopus-secret/access.log
sudo tail -f /var/log/autopus-secret/error.log

# Logs de Nginx
sudo tail -f /var/log/nginx/secret-autopus-access.log
sudo tail -f /var/log/nginx/secret-autopus-error.log
```

### Detener la aplicación

```bash
sudo supervisorctl stop autopus-secret-api
```

### Ver estado

```bash
sudo supervisorctl status autopus-secret-api
```

### Actualizar código (deploy nuevas versiones)

```bash
# Como usuario autopus
cd ~/autopus-secret-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
exit

# Reiniciar servicio
sudo supervisorctl restart autopus-secret-api
```

---

## 🔐 Paso 8: Configuraciones de seguridad adicionales

### 8.1 Configurar firewall (UFW)

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

### 8.2 Configurar fail2ban (protección contra brute force)

```bash
sudo apt install -y fail2ban

# Copiar configuración
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Editar configuración
sudo nano /etc/fail2ban/jail.local
```

Asegúrate de que esté habilitado:
```ini
[sshd]
enabled = true

[nginx-http-auth]
enabled = true
```

Reiniciar fail2ban:
```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

### 8.3 Configurar actualizaciones automáticas de seguridad

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 Paso 9: Monitoring opcional

### 9.1 Instalar htop (monitoreo de procesos)

```bash
sudo apt install -y htop
htop
```

### 9.2 Configurar alertas de disco lleno

```bash
sudo apt install -y smartmontools
```

### 9.3 Crear script de backup de logs

```bash
sudo nano /usr/local/bin/backup-logs.sh
```

Contenido:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /home/autopus/backups/logs-$DATE.tar.gz /var/log/autopus-secret/
find /home/autopus/backups/ -name "logs-*.tar.gz" -mtime +7 -delete
```

Dar permisos:
```bash
sudo chmod +x /usr/local/bin/backup-logs.sh
```

Crear cron job:
```bash
sudo crontab -e
```

Agregar:
```
0 2 * * * /usr/local/bin/backup-logs.sh
```

---

## 🧪 Paso 10: Testing en producción

### 10.1 Test con curl

```bash
# Crear secreto
TOKEN=$(curl -X POST "https://secret.autopus.es/api/secret" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hola producción", "ttl_minutes": 5}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# Leer secreto
curl "https://secret.autopus.es/api/secret/$TOKEN"
```

### 10.2 Test admin endpoints

```bash
curl "https://secret.autopus.es/admin/stats" \
  -H "X-API-Key: tu-api-key-admin"
```

---

## 🆘 Troubleshooting

### La API no responde

```bash
# Verificar que esté corriendo
sudo supervisorctl status autopus-secret-api

# Ver logs
sudo tail -50 /var/log/autopus-secret/error.log

# Reiniciar
sudo supervisorctl restart autopus-secret-api
```

### Error 502 Bad Gateway

```bash
# Verificar que el puerto 8000 esté escuchando
sudo netstat -tulpn | grep 8000

# Verificar logs de Nginx
sudo tail -50 /var/log/nginx/secret-autopus-error.log
```

### SSL no funciona

```bash
# Verificar certificados
sudo certbot certificates

# Renovar manualmente
sudo certbot renew --force-renewal
```

### Puerto 8000 ya en uso

```bash
# Ver qué proceso está usando el puerto
sudo lsof -i :8000

# Matar proceso si es necesario
sudo kill -9 PID
```

---

## 📝 Checklist final

- [ ] VPS actualizado
- [ ] Python 3.9+ instalado
- [ ] Nginx instalado y configurado
- [ ] Supervisor configurado
- [ ] Código clonado
- [ ] .env configurado con valores de producción
- [ ] Variables de entorno correctas (ENVIRONMENT=production)
- [ ] SSL/HTTPS configurado
- [ ] Dominio apuntando al VPS
- [ ] Firewall configurado
- [ ] API corriendo con Supervisor
- [ ] Logs funcionando
- [ ] Endpoints públicos funcionan
- [ ] Endpoints admin funcionan con API Key
- [ ] Swagger UI accesible en /docs
- [ ] Health check funciona

---

## 🎉 ¡Listo!

Tu API está en producción en:
- **URL**: https://secret.autopus.es
- **Docs**: https://secret.autopus.es/docs
- **Health**: https://secret.autopus.es/health

---

## 📚 Recursos adicionales

- [Documentación de Nginx](https://nginx.org/en/docs/)
- [Documentación de Supervisor](http://supervisord.org/)
- [Documentación de Certbot](https://certbot.eff.org/)
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)

---

**Autor**: Autopus  
**Fecha**: 2025-11-04  
**Versión**: 1.0.0
