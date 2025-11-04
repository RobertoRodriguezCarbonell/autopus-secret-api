"""
Router de endpoints administrativos (protegidos por API Key)
"""
from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
from datetime import datetime
import logging

from app.config import settings
from app.services.database import database_service
from app.scheduler import get_scheduler_status
from app.utils.datetime_utils import now_spain, spain_to_utc

router = APIRouter()
logger = logging.getLogger(__name__)


def verify_admin_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Dependency para verificar API Key en endpoints administrativos
    
    Header requerido: X-API-Key: <tu-api-key>
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key requerida en header X-API-Key"
        )
    
    # Verificar token directamente
    if x_api_key != settings.api_key_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida"
        )
    
    return True


@router.get("/stats", dependencies=[Depends(verify_admin_key)])
async def get_stats():
    """
    Obtener estadísticas globales del sistema
    
    Requiere: Authorization: Bearer <API_KEY>
    
    Retorna:
    - Total de secretos activos
    - Total de secretos accedidos
    - Total de secretos expirados
    - Secretos con passphrase
    """
    try:
        # Obtener todos los secretos para calcular estadísticas
        from supabase import PostgrestAPIError
        
        # Total de secretos activos (no destruidos y no expirados)
        # Usar UTC para comparar con la base de datos
        current_time_utc = spain_to_utc(now_spain()).isoformat()
        active_response = await database_service.client.table("secrets")\
            .select("*", count="exact")\
            .eq("is_destroyed", False)\
            .gte("expires_at", current_time_utc)\
            .execute()
        total_active = active_response.count if hasattr(active_response, 'count') else len(active_response.data)
        
        # Total de secretos accedidos (destruidos por lectura)
        accessed_response = await database_service.client.table("secrets")\
            .select("*", count="exact")\
            .eq("is_destroyed", True)\
            .not_.is_("accessed_at", "null")\
            .execute()
        total_accessed = accessed_response.count if hasattr(accessed_response, 'count') else len(accessed_response.data)
        
        # Total de secretos expirados
        expired_response = await database_service.client.table("secrets")\
            .select("*", count="exact")\
            .lt("expires_at", current_time_utc)\
            .execute()
        total_expired = expired_response.count if hasattr(expired_response, 'count') else len(expired_response.data)
        
        # Secretos con passphrase
        protected_response = await database_service.client.table("secrets")\
            .select("*", count="exact")\
            .not_.is_("passphrase_hash", "null")\
            .execute()
        total_protected = protected_response.count if hasattr(protected_response, 'count') else len(protected_response.data)
        
        # Total general
        all_response = await database_service.client.table("secrets")\
            .select("*", count="exact")\
            .execute()
        total_all = all_response.count if hasattr(all_response, 'count') else len(all_response.data)
        
        logger.info("📊 Estadísticas solicitadas por administrador")
        
        return {
            "timestamp": now_spain().isoformat(),
            "statistics": {
                "total_secrets": total_all,
                "active_secrets": total_active,
                "accessed_secrets": total_accessed,
                "expired_secrets": total_expired,
                "protected_secrets": total_protected
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas"
        )


@router.delete("/system/purge", dependencies=[Depends(verify_admin_key)])
async def purge_expired():
    """
    Forzar limpieza de secretos expirados
    
    Requiere: Authorization: Bearer <API_KEY>
    
    Elimina todos los secretos que hayan expirado
    """
    try:
        logger.info("🧹 Limpieza manual de secretos expirados iniciada por administrador")
        
        # Obtener secretos expirados antes de eliminar
        expired_secrets = await database_service.get_expired_secrets()
        count_before = len(expired_secrets)
        
        # Purgar secretos expirados
        deleted_count = await database_service.purge_expired()
        
        logger.info(f"✅ Limpieza completada: {deleted_count} secretos eliminados")
        
        return {
            "success": True,
            "message": "Limpieza completada",
            "deleted_count": deleted_count,
            "timestamp": now_spain().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error durante limpieza manual: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al ejecutar limpieza"
        )


@router.get("/system/health", dependencies=[Depends(verify_admin_key)])
async def system_health():
    """
    Verificar estado del sistema (DB, Scheduler, etc.)
    
    Requiere: Authorization: Bearer <API_KEY>
    
    Retorna el estado de:
    - Conexión a base de datos
    - Scheduler y jobs programados
    - Servicio de cifrado
    """
    health_status = {
        "timestamp": now_spain().isoformat(),
        "status": "healthy",
        "components": {}
    }
    
    # Verificar base de datos
    try:
        test_response = await database_service.client.table("secrets")\
            .select("id")\
            .limit(1)\
            .execute()
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Conexión exitosa"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # Verificar scheduler
    try:
        scheduler_status = get_scheduler_status()
        health_status["components"]["scheduler"] = {
            "status": "healthy" if scheduler_status["running"] else "stopped",
            "jobs": scheduler_status["jobs"]
        }
        if not scheduler_status["running"]:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["scheduler"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Verificar servicio de cifrado
    try:
        from app.services.encryption import encryption_service
        test_text = "health_check"
        encrypted = encryption_service.encrypt(test_text)
        decrypted = encryption_service.decrypt(encrypted)
        
        health_status["components"]["encryption"] = {
            "status": "healthy" if decrypted == test_text else "unhealthy",
            "message": "Cifrado/descifrado funcionando correctamente"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["encryption"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    logger.info(f"🏥 Health check ejecutado - Estado: {health_status['status']}")
    
    return health_status


@router.get("/system/info", dependencies=[Depends(verify_admin_key)])
async def system_info():
    """
    Información del sistema (versión, uptime, entorno)
    
    Requiere: Authorization: Bearer <API_KEY>
    
    Retorna información general del sistema y configuración
    """
    import sys
    import platform
    
    info = {
        "api": {
            "title": settings.api_title,
            "version": settings.api_version,
            "environment": settings.environment
        },
        "system": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "architecture": platform.machine()
        },
        "configuration": {
            "max_secret_size_mb": settings.max_secret_size / (1024 * 1024),
            "min_ttl_minutes": settings.min_ttl_minutes,
            "max_ttl_minutes": settings.max_ttl_minutes,
            "default_ttl_minutes": settings.default_ttl_minutes,
            "min_passphrase_length": settings.min_passphrase_length,
            "cors_enabled": len(settings.cors_origins_list) > 0
        },
        "scheduler": get_scheduler_status(),
        "timestamp": now_spain().isoformat()
    }
    
    logger.info("ℹ️ Información del sistema solicitada por administrador")
    
    return info
