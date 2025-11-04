"""
Router de endpoints públicos para gestión de secretos
"""
from fastapi import APIRouter, HTTPException, status, Request
from datetime import datetime
import logging

from app.schemas.secret import (
    SecretCreateRequest,
    SecretCreateResponse,
    SecretReadResponse,
    SecretDeleteResponse,
    SecretVerifyRequest,
    SecretVerifyResponse
)
from app.services.database import database_service
from app.services.encryption import encryption_service
from app.utils.token_generator import generate_unique_token
from app.utils.validators import calculate_expiration
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/secret", status_code=status.HTTP_201_CREATED, response_model=SecretCreateResponse)
async def create_secret(request: Request, secret_request: SecretCreateRequest):
    """
    Crear un nuevo secreto cifrado
    
    - **content**: Texto del secreto a cifrar (máx 10KB)
    - **ttl_minutes**: Tiempo de vida en minutos (5-10080, default 60)
    - **passphrase**: Contraseña opcional para proteger el secreto (mín 6 caracteres)
    
    Retorna el token único y URL para acceder al secreto
    """
    try:
        # 1. Generar token único
        token = await generate_unique_token(database_service)
        logger.info(f"Token generado para nuevo secreto: {token[:10]}...")
        
        # 2. Cifrar contenido
        encrypted_content = encryption_service.encrypt(secret_request.content)
        logger.debug("Contenido cifrado correctamente")
        
        # 3. Hash de passphrase (si existe)
        passphrase_hash = None
        if secret_request.passphrase:
            passphrase_hash = encryption_service.hash_passphrase(secret_request.passphrase)
            logger.debug("Passphrase hasheada correctamente")
        
        # 4. Calcular fecha de expiración
        expires_at = calculate_expiration(secret_request.ttl_minutes)
        
        # 5. Guardar en Supabase
        result = await database_service.create_secret(
            token=token,
            encrypted_content=encrypted_content,
            expires_at=expires_at,
            passphrase_hash=passphrase_hash,
            metadata={
                "ttl_minutes": secret_request.ttl_minutes,
                "has_passphrase": passphrase_hash is not None,
                "content_length": len(secret_request.content)
            }
        )
        
        # 6. Construir URL completa
        base_url = str(request.base_url).rstrip('/')
        secret_url = f"{base_url}/api/secret/{token}"
        
        logger.info(f"Secreto creado exitosamente: {token[:10]}... | Expira: {expires_at}")
        
        # 7. Retornar respuesta
        return SecretCreateResponse(
            token=token,
            url=secret_url,
            expires_at=expires_at,
            has_passphrase=passphrase_hash is not None
        )
        
    except ValueError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al crear secreto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el secreto"
        )


@router.get("/secret/{token}", response_model=SecretReadResponse)
async def get_secret(token: str, passphrase: str = None):
    """
    Obtener y destruir un secreto (acceso único)
    
    - **token**: Token único del secreto
    - **passphrase**: Contraseña (si fue protegido) - Query parameter opcional
    
    El secreto se marca como destruido después de la lectura
    
    **⚠️ IMPORTANTE**: Este endpoint solo puede usarse una vez. Después de leer el secreto, 
    se destruirá automáticamente y no podrá volver a accederse.
    """
    try:
        # 1. Buscar secreto por token
        secret_data = await database_service.get_secret_by_token(token)
        
        if not secret_data:
            logger.warning(f"Intento de acceso a secreto inexistente: {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secreto no encontrado o ya fue destruido"
            )
        
        # 2. Validar que no esté destruido
        if secret_data['is_destroyed']:
            logger.warning(f"Intento de acceso a secreto ya destruido: {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Este secreto ya fue accedido y destruido"
            )
        
        # 3. Validar que no haya expirado
        expires_at = datetime.fromisoformat(secret_data['expires_at'].replace('Z', '+00:00'))
        if datetime.now(expires_at.tzinfo) > expires_at:
            logger.warning(f"Intento de acceso a secreto expirado: {token[:10]}...")
            # Marcar como destruido
            await database_service.mark_as_accessed(token)
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Este secreto ha expirado"
            )
        
        # 4. Validar passphrase (si es requerida)
        if secret_data['passphrase_hash']:
            if not passphrase:
                logger.warning(f"Intento de acceso sin passphrase: {token[:10]}...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Este secreto requiere una passphrase. Proporciona el parámetro ?passphrase=tu-clave"
                )
            
            if not encryption_service.verify_passphrase(passphrase, secret_data['passphrase_hash']):
                logger.warning(f"Passphrase incorrecta para: {token[:10]}...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Passphrase incorrecta"
                )
        
        # 5. Descifrar contenido
        try:
            decrypted_content = encryption_service.decrypt(secret_data['encrypted_content'])
        except Exception as e:
            logger.error(f"Error al descifrar secreto {token[:10]}...: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al descifrar el secreto"
            )
        
        # 6. Marcar como destruido (accessed_at = NOW, is_destroyed = TRUE)
        await database_service.mark_as_accessed(token)
        
        created_at = datetime.fromisoformat(secret_data['created_at'].replace('Z', '+00:00'))
        
        logger.info(f"Secreto accedido y destruido: {token[:10]}... | Creado: {created_at}")
        
        # 7. Retornar contenido descifrado
        return SecretReadResponse(
            content=decrypted_content,
            created_at=created_at,
            message="⚠️ Este secreto ha sido destruido y no puede volver a ser accedido"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener secreto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud"
        )


@router.delete("/secret/{token}/delete", response_model=SecretDeleteResponse)
async def delete_secret(token: str):
    """
    Destruir manualmente un secreto sin leerlo
    
    - **token**: Token único del secreto
    
    Útil cuando quieres asegurarte de que un secreto no pueda ser accedido
    sin necesidad de leerlo primero.
    """
    try:
        # 1. Buscar secreto por token
        secret_data = await database_service.get_secret_by_token(token)
        
        if not secret_data:
            logger.warning(f"Intento de eliminar secreto inexistente: {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secreto no encontrado"
            )
        
        # 2. Verificar si ya está destruido
        if secret_data['is_destroyed']:
            logger.info(f"Secreto ya estaba destruido: {token[:10]}...")
            return SecretDeleteResponse(
                success=True,
                message="El secreto ya estaba destruido previamente"
            )
        
        # 3. Marcar como destruido
        await database_service.delete_secret(token)
        
        logger.info(f"Secreto destruido manualmente: {token[:10]}...")
        
        return SecretDeleteResponse(
            success=True,
            message="Secreto destruido exitosamente sin ser leído"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar secreto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el secreto"
        )


@router.post("/secret/verify", response_model=SecretVerifyResponse)
async def verify_passphrase(verify_request: SecretVerifyRequest):
    """
    Verificar si una passphrase es correcta sin revelar el secreto
    
    - **token**: Token único del secreto
    - **passphrase**: Contraseña a verificar
    
    Útil para validar que tienes la passphrase correcta antes de consumir
    el acceso único del secreto.
    
    **Nota**: Este endpoint NO marca el secreto como destruido.
    """
    try:
        # 1. Buscar secreto por token
        secret_data = await database_service.get_secret_by_token(verify_request.token)
        
        if not secret_data:
            logger.warning(f"Intento de verificar passphrase de secreto inexistente: {verify_request.token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secreto no encontrado"
            )
        
        # 2. Validar que no esté destruido
        if secret_data['is_destroyed']:
            return SecretVerifyResponse(
                valid=False,
                message="El secreto ya fue destruido"
            )
        
        # 3. Verificar si tiene passphrase
        if not secret_data['passphrase_hash']:
            return SecretVerifyResponse(
                valid=True,
                message="Este secreto no tiene passphrase protegida"
            )
        
        # 4. Verificar passphrase
        is_valid = encryption_service.verify_passphrase(
            verify_request.passphrase,
            secret_data['passphrase_hash']
        )
        
        if is_valid:
            logger.info(f"Passphrase verificada correctamente: {verify_request.token[:10]}...")
            return SecretVerifyResponse(
                valid=True,
                message="Passphrase correcta"
            )
        else:
            logger.warning(f"Passphrase incorrecta en verificación: {verify_request.token[:10]}...")
            return SecretVerifyResponse(
                valid=False,
                message="Passphrase incorrecta"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al verificar passphrase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar la passphrase"
        )
