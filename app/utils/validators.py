"""
Validadores personalizados para la API
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.config import settings
from app.utils.datetime_utils import now_spain

logger = logging.getLogger(__name__)


def validate_ttl(ttl_minutes: int) -> bool:
    """
    Valida que el TTL esté dentro del rango permitido
    
    Args:
        ttl_minutes: Tiempo de vida en minutos
        
    Returns:
        True si es válido
        
    Raises:
        ValueError: Si el TTL está fuera de rango
    """
    if ttl_minutes < settings.min_ttl_minutes:
        raise ValueError(
            f"TTL mínimo permitido: {settings.min_ttl_minutes} minutos"
        )
    
    if ttl_minutes > settings.max_ttl_minutes:
        raise ValueError(
            f"TTL máximo permitido: {settings.max_ttl_minutes} minutos ({settings.max_ttl_minutes // 1440} días)"
        )
    
    return True


def calculate_expiration(ttl_minutes: int) -> datetime:
    """
    Calcula la fecha de expiración basada en el TTL
    
    Args:
        ttl_minutes: Tiempo de vida en minutos
        
    Returns:
        Fecha y hora de expiración en zona horaria de España
    """
    validate_ttl(ttl_minutes)
    expiration = now_spain() + timedelta(minutes=ttl_minutes)
    logger.debug(f"Expiración calculada: {expiration}")
    return expiration


def validate_content_size(content: str) -> bool:
    """
    Valida que el contenido no exceda el tamaño máximo
    
    Args:
        content: Contenido del secreto
        
    Returns:
        True si es válido
        
    Raises:
        ValueError: Si el contenido excede el tamaño máximo
    """
    size_bytes = len(content.encode('utf-8'))
    
    if size_bytes > settings.max_secret_size_bytes:
        raise ValueError(
            f"El contenido excede el tamaño máximo de {settings.max_secret_size_kb}KB"
        )
    
    return True


def validate_passphrase(passphrase: Optional[str]) -> bool:
    """
    Valida que la passphrase cumpla con los requisitos mínimos
    
    Args:
        passphrase: Contraseña a validar (puede ser None)
        
    Returns:
        True si es válida o None
        
    Raises:
        ValueError: Si la passphrase no cumple requisitos
    """
    if passphrase is None:
        return True
    
    if len(passphrase) < 6:
        raise ValueError("La passphrase debe tener al menos 6 caracteres")
    
    return True
