"""
Scheduler para tareas programadas
Ejecuta limpieza de secretos expirados cada hora
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.services.database import database_service
from app.config import settings

logger = logging.getLogger(__name__)

# Crear scheduler global
scheduler = AsyncIOScheduler()


async def cleanup_expired_secrets():
    """
    Tarea programada para eliminar secretos expirados
    Se ejecuta cada hora
    """
    try:
        logger.info("🧹 Iniciando limpieza de secretos expirados...")
        
        # Obtener secretos expirados
        expired_secrets = await database_service.get_expired_secrets()
        
        if not expired_secrets:
            logger.info("✅ No hay secretos expirados para limpiar")
            return
        
        # Purgar secretos expirados
        deleted_count = await database_service.purge_expired()
        
        logger.info(f"✅ Limpieza completada: {deleted_count} secretos eliminados")
        
    except Exception as e:
        logger.error(f"❌ Error durante la limpieza de secretos: {e}")


def start_scheduler():
    """
    Iniciar el scheduler con todas las tareas programadas
    """
    try:
        # Agregar job de limpieza cada hora
        scheduler.add_job(
            cleanup_expired_secrets,
            trigger=CronTrigger(minute=0),  # Se ejecuta al minuto 0 de cada hora
            id='cleanup_expired_secrets',
            name='Limpiar secretos expirados',
            replace_existing=True,
            misfire_grace_time=300  # 5 minutos de gracia si se pierde la ejecución
        )
        
        # Iniciar scheduler
        scheduler.start()
        logger.info("⏰ Scheduler iniciado correctamente")
        logger.info("📅 Job 'cleanup_expired_secrets' programado cada hora")
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar scheduler: {e}")
        raise


def shutdown_scheduler():
    """
    Detener el scheduler de forma segura
    """
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info("⏰ Scheduler detenido correctamente")
    except Exception as e:
        logger.error(f"❌ Error al detener scheduler: {e}")


def get_scheduler_status():
    """
    Obtener estado actual del scheduler y sus jobs
    
    Returns:
        dict: Información del scheduler y sus jobs
    """
    if not scheduler.running:
        return {
            "running": False,
            "jobs": []
        }
    
    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "running": True,
        "jobs": jobs_info
    }
