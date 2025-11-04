"""
Utilidades para manejo de fechas y tiempos con timezone España
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Zona horaria de España
SPAIN_TZ = ZoneInfo("Europe/Madrid")


def now_spain() -> datetime:
    """
    Retorna la fecha/hora actual en zona horaria de España
    
    Returns:
        datetime con timezone Europe/Madrid
    """
    return datetime.now(SPAIN_TZ)


def utc_to_spain(dt: datetime) -> datetime:
    """
    Convierte un datetime UTC a zona horaria de España
    
    Args:
        dt: datetime en UTC
        
    Returns:
        datetime en Europe/Madrid
    """
    if dt.tzinfo is None:
        # Si no tiene timezone, asumimos que es UTC
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(SPAIN_TZ)


def spain_to_utc(dt: datetime) -> datetime:
    """
    Convierte un datetime de España a UTC
    
    Args:
        dt: datetime en Europe/Madrid
        
    Returns:
        datetime en UTC
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SPAIN_TZ)
    return dt.astimezone(ZoneInfo("UTC"))


def format_spain_datetime(dt: datetime) -> str:
    """
    Formatea un datetime en zona horaria de España
    
    Args:
        dt: datetime a formatear
        
    Returns:
        String ISO 8601 con timezone
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SPAIN_TZ)
    return dt.isoformat()


def parse_datetime(date_string: str) -> datetime:
    """
    Parsea un string de fecha a datetime con timezone
    
    Args:
        date_string: String de fecha en formato ISO
        
    Returns:
        datetime parseado
    """
    dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SPAIN_TZ)
    return dt
