"""
Schemas de validación para secretos (DTOs)
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

from app.config import settings


class SecretCreateRequest(BaseModel):
    """
    DTO para crear un nuevo secreto
    """
    content: str = Field(
        ...,
        description="Contenido del secreto a cifrar",
        min_length=1,
        max_length=settings.max_secret_size_kb * 1024
    )
    ttl_minutes: int = Field(
        default=60,
        description="Tiempo de vida en minutos",
        ge=settings.min_ttl_minutes,
        le=settings.max_ttl_minutes
    )
    passphrase: Optional[str] = Field(
        None,
        description="Contraseña opcional para proteger el secreto",
        min_length=6
    )
    
    @validator('content')
    def validate_content_size(cls, v):
        """
        Valida que el contenido no exceda el tamaño máximo
        """
        size_bytes = len(v.encode('utf-8'))
        if size_bytes > settings.max_secret_size_bytes:
            raise ValueError(
                f"El contenido excede el tamaño máximo de {settings.max_secret_size_kb}KB"
            )
        return v


class SecretCreateResponse(BaseModel):
    """
    DTO de respuesta al crear un secreto
    """
    token: str = Field(..., description="Token único del secreto")
    url: str = Field(..., description="URL completa para acceder al secreto")
    expires_at: datetime = Field(..., description="Fecha y hora de expiración")
    has_passphrase: bool = Field(..., description="Indica si el secreto está protegido por contraseña")


class SecretReadResponse(BaseModel):
    """
    DTO de respuesta al leer un secreto
    """
    content: str = Field(..., description="Contenido descifrado del secreto")
    created_at: datetime = Field(..., description="Fecha de creación")
    message: str = Field(
        default="Este secreto ha sido destruido y no puede volver a ser accedido",
        description="Mensaje informativo"
    )


class SecretVerifyRequest(BaseModel):
    """
    DTO para verificar una passphrase
    """
    token: str = Field(..., description="Token del secreto")
    passphrase: str = Field(..., description="Contraseña a verificar")


class SecretVerifyResponse(BaseModel):
    """
    DTO de respuesta al verificar passphrase
    """
    valid: bool = Field(..., description="Indica si la passphrase es válida")
    message: str = Field(..., description="Mensaje descriptivo")


class SecretDeleteResponse(BaseModel):
    """
    DTO de respuesta al eliminar un secreto
    """
    success: bool = Field(..., description="Indica si la eliminación fue exitosa")
    message: str = Field(..., description="Mensaje confirmando la eliminación")
