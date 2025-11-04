#!/bin/bash

# ============================================
# Script de Deployment Automático
# Autopus Secret API
# ============================================

set -e  # Exit on error

echo "🚀 Iniciando deployment de Autopus Secret API..."
echo ""

# Variables
PROJECT_DIR="/home/autopus/autopus-secret-api"
VENV_DIR="$PROJECT_DIR/venv"
BRANCH="main"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funciones
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar si estamos en el directorio correcto
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Directorio del proyecto no encontrado: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"
log_success "Directorio del proyecto: $PROJECT_DIR"

# 1. Backup del .env actual
echo ""
echo "📦 Haciendo backup de .env..."
if [ -f .env ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    log_success "Backup de .env creado"
else
    log_warning "No se encontró archivo .env"
fi

# 2. Pull del código
echo ""
echo "📥 Descargando últimos cambios..."
git fetch origin
git pull origin $BRANCH
log_success "Código actualizado desde branch: $BRANCH"

# 3. Activar entorno virtual
echo ""
echo "🔧 Activando entorno virtual..."
source "$VENV_DIR/bin/activate"
log_success "Entorno virtual activado"

# 4. Actualizar dependencias
echo ""
echo "📚 Actualizando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
log_success "Dependencias actualizadas"

# 5. Verificar .env
echo ""
echo "🔍 Verificando configuración..."
if [ ! -f .env ]; then
    log_error "Archivo .env no encontrado. Copia .env.example y configúralo."
    exit 1
fi

# Verificar variables críticas
required_vars=("SUPABASE_URL" "SUPABASE_KEY" "ENCRYPTION_KEY" "API_KEY_ADMIN")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^$var=" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    log_error "Variables faltantes en .env: ${missing_vars[*]}"
    exit 1
fi

log_success "Configuración verificada"

# 6. Test rápido (opcional)
echo ""
echo "🧪 Ejecutando tests..."
if [ -d "tests" ]; then
    python -m pytest tests/ -v --tb=short 2>/dev/null || log_warning "Tests fallaron o pytest no disponible"
else
    log_warning "No se encontró directorio de tests"
fi

# 7. Reiniciar servicio
echo ""
echo "🔄 Reiniciando servicio..."
sudo supervisorctl restart autopus-secret-api

# Esperar un momento para que el servicio inicie
sleep 2

# 8. Verificar que el servicio esté corriendo
echo ""
echo "✔️  Verificando estado del servicio..."
status=$(sudo supervisorctl status autopus-secret-api | awk '{print $2}')

if [ "$status" = "RUNNING" ]; then
    log_success "Servicio corriendo correctamente"
else
    log_error "Servicio no está corriendo. Estado: $status"
    echo ""
    echo "Ver logs con: sudo tail -f /var/log/autopus-secret/error.log"
    exit 1
fi

# 9. Health check
echo ""
echo "🏥 Verificando health check..."
sleep 2
response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)

if [ "$response" = "200" ]; then
    log_success "Health check OK (HTTP $response)"
else
    log_error "Health check failed (HTTP $response)"
    exit 1
fi

# 10. Verificar versión desplegada
echo ""
echo "📊 Información de deployment:"
echo "-----------------------------------"
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Usuario: $(whoami)"
echo "Branch: $BRANCH"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Mensaje: $(git log -1 --pretty=%B)"
echo "-----------------------------------"

# 11. Mostrar logs recientes
echo ""
echo "📜 Últimas líneas de logs:"
echo "-----------------------------------"
sudo tail -10 /var/log/autopus-secret/access.log
echo "-----------------------------------"

# 12. Instrucciones finales
echo ""
log_success "🎉 Deployment completado exitosamente!"
echo ""
echo "URLs disponibles:"
echo "  - API: https://secret.autopus.es"
echo "  - Docs: https://secret.autopus.es/docs"
echo "  - Health: https://secret.autopus.es/health"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: sudo tail -f /var/log/autopus-secret/error.log"
echo "  - Estado: sudo supervisorctl status autopus-secret-api"
echo "  - Reiniciar: sudo supervisorctl restart autopus-secret-api"
echo ""
