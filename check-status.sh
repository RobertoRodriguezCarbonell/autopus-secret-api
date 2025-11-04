#!/bin/bash

# ============================================
# Script de Verificación de Estado
# Autopus Secret API
# ============================================

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🔍 Estado de Autopus Secret API${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. Estado del servicio Supervisor
echo -e "${YELLOW}📊 Servicio (Supervisor):${NC}"
sudo supervisorctl status autopus-secret-api
echo ""

# 2. Proceso de Python
echo -e "${YELLOW}🐍 Procesos Python:${NC}"
ps aux | grep "[u]vicorn app.main:app" | head -n 3
echo ""

# 3. Puerto 8000
echo -e "${YELLOW}🔌 Puerto 8000:${NC}"
sudo netstat -tulpn | grep ":8000" || echo "No listening"
echo ""

# 4. Estado de Nginx
echo -e "${YELLOW}🌐 Nginx:${NC}"
sudo systemctl status nginx | grep "Active:"
echo ""

# 5. Certificado SSL
echo -e "${YELLOW}🔒 Certificado SSL:${NC}"
sudo certbot certificates 2>/dev/null | grep -A 5 "secret.autopus.es" || echo "No encontrado"
echo ""

# 6. Health check local
echo -e "${YELLOW}🏥 Health Check (local):${NC}"
response=$(curl -s http://127.0.0.1:8000/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ OK${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
else
    echo -e "${RED}❌ FAILED${NC}"
fi
echo ""

# 7. Health check público
echo -e "${YELLOW}🌍 Health Check (público):${NC}"
response=$(curl -s https://secret.autopus.es/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ OK${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
else
    echo -e "${RED}❌ FAILED${NC}"
fi
echo ""

# 8. Últimos logs de error
echo -e "${YELLOW}📜 Últimos errores (si hay):${NC}"
sudo tail -5 /var/log/autopus-secret/error.log 2>/dev/null || echo "No hay logs de error recientes"
echo ""

# 9. Uso de disco
echo -e "${YELLOW}💾 Uso de disco:${NC}"
df -h | grep -E "Filesystem|/$"
echo ""

# 10. Memoria
echo -e "${YELLOW}🧠 Uso de memoria:${NC}"
free -h
echo ""

# 11. Uptime
echo -e "${YELLOW}⏱️  Uptime del servidor:${NC}"
uptime
echo ""

# 12. Git info
echo -e "${YELLOW}📦 Versión desplegada:${NC}"
cd /home/autopus/autopus-secret-api 2>/dev/null && {
    echo "Branch: $(git rev-parse --abbrev-ref HEAD)"
    echo "Commit: $(git rev-parse --short HEAD)"
    echo "Fecha: $(git log -1 --format=%cd)"
} || echo "No disponible"
echo ""

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ Verificación completada${NC}"
echo -e "${BLUE}================================${NC}"
