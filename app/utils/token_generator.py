"""
Generador de tokens únicos y seguros para los secretos
"""
import secrets
import logging

logger = logging.getLogger(__name__)


def generate_token(length: int = 48) -> str:
    """
    Genera un token único y seguro usando secrets
    
    Args:
        length: Longitud del token en bytes (default: 48)
        
    Returns:
        Token URL-safe en base64 (aproximadamente 64 caracteres)
    """
    try:
        token = secrets.token_urlsafe(length)
        logger.debug(f"Token generado: {token[:10]}...")
        return token
    except Exception as e:
        logger.error(f"Error al generar token: {e}")
        raise


async def generate_unique_token(db_service, max_attempts: int = 5) -> str:
    """
    Genera un token único verificando que no exista en la base de datos
    
    Args:
        db_service: Instancia del servicio de base de datos
        max_attempts: Máximo de intentos para generar un token único
        
    Returns:
        Token único verificado
        
    Raises:
        RuntimeError: Si no se puede generar un token único después de max_attempts
    """
    for attempt in range(max_attempts):
        token = generate_token()
        
        # Verificar si el token ya existe
        existing = await db_service.get_secret_by_token(token)
        
        if not existing:
            logger.info(f"✅ Token único generado en intento {attempt + 1}")
            return token
        
        logger.warning(f"⚠️ Token duplicado encontrado en intento {attempt + 1}")
    
    # Si después de max_attempts no se generó un token único
    logger.error(f"❌ No se pudo generar token único después de {max_attempts} intentos")
    raise RuntimeError("No se pudo generar un token único")
