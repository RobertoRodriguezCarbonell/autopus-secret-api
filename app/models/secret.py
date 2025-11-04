"""
Modelos de dominio para secretos
"""
from datetime import datetime
from typing import Optional
from uuid import UUID


class Secret:
    """
    Modelo de dominio que representa un secreto en el sistema
    """
    def __init__(
        self,
        id: UUID,
        token: str,
        encrypted_content: str,
        expires_at: datetime,
        created_at: datetime,
        passphrase_hash: Optional[str] = None,
        accessed_at: Optional[datetime] = None,
        is_destroyed: bool = False,
        metadata: Optional[dict] = None
    ):
        self.id = id
        self.token = token
        self.encrypted_content = encrypted_content
        self.expires_at = expires_at
        self.created_at = created_at
        self.passphrase_hash = passphrase_hash
        self.accessed_at = accessed_at
        self.is_destroyed = is_destroyed
        self.metadata = metadata or {}
    
    def is_expired(self) -> bool:
        """
        Verifica si el secreto ha expirado
        """
        return datetime.utcnow() > self.expires_at
    
    def is_accessible(self) -> bool:
        """
        Verifica si el secreto es accesible (no destruido y no expirado)
        """
        return not self.is_destroyed and not self.is_expired()
