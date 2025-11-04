"""
Cliente de Supabase para operaciones de base de datos
"""
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from app.config import settings
from app.utils.datetime_utils import now_spain, spain_to_utc

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Servicio para interactuar con Supabase
    """
    
    def __init__(self):
        """
        Inicializa el cliente de Supabase
        """
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("✅ Cliente de Supabase inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error al inicializar cliente de Supabase: {e}")
            raise
    
    async def create_secret(
        self,
        token: str,
        encrypted_content: str,
        expires_at: datetime,
        passphrase_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo secreto en la base de datos
        
        Args:
            token: Token único del secreto
            encrypted_content: Contenido cifrado
            expires_at: Fecha de expiración
            passphrase_hash: Hash de la passphrase (opcional)
            metadata: Metadatos adicionales (opcional)
            
        Returns:
            Datos del secreto creado
        """
        try:
            # Convertir fecha de España a UTC para guardar en Supabase
            expires_at_utc = spain_to_utc(expires_at)
            
            data = {
                "token": token,
                "encrypted_content": encrypted_content,
                "expires_at": expires_at_utc.isoformat(),
                "passphrase_hash": passphrase_hash,
                "metadata": metadata or {}
            }
            
            result = self.client.table("secrets").insert(data).execute()
            logger.info(f"✅ Secreto creado con token: {token}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Error al crear secreto: {e}")
            raise
    
    async def get_secret_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un secreto por su token
        
        Args:
            token: Token único del secreto
            
        Returns:
            Datos del secreto o None si no existe
        """
        try:
            result = self.client.table("secrets").select("*").eq("token", token).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error al obtener secreto: {e}")
            raise
    
    async def mark_as_accessed(self, token: str) -> bool:
        """
        Marca un secreto como accedido (destruido)
        
        Args:
            token: Token único del secreto
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Guardar en UTC
            accessed_at_utc = spain_to_utc(now_spain())
            
            result = self.client.table("secrets").update({
                "accessed_at": accessed_at_utc.isoformat(),
                "is_destroyed": True
            }).eq("token", token).execute()
            
            logger.info(f"✅ Secreto {token} marcado como destruido")
            return True
        except Exception as e:
            logger.error(f"❌ Error al marcar secreto como accedido: {e}")
            raise
    
    async def delete_secret(self, token: str) -> bool:
        """
        Elimina un secreto de la base de datos
        
        Args:
            token: Token único del secreto
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            # Primero marcamos como destruido
            self.client.table("secrets").update({
                "is_destroyed": True
            }).eq("token", token).execute()
            
            logger.info(f"✅ Secreto {token} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error al eliminar secreto: {e}")
            raise
    
    async def get_expired_secrets(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los secretos expirados
        
        Returns:
            Lista de secretos expirados
        """
        try:
            # Comparar con UTC ya que en DB está en UTC
            now_utc = spain_to_utc(now_spain()).isoformat()
            result = self.client.table("secrets").select("*").lt("expires_at", now_utc).execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ Error al obtener secretos expirados: {e}")
            raise
    
    async def purge_expired(self) -> int:
        """
        Elimina todos los secretos expirados de la base de datos
        
        Returns:
            Cantidad de secretos eliminados
        """
        try:
            # Comparar con UTC ya que en DB está en UTC
            now_utc = spain_to_utc(now_spain()).isoformat()
            result = self.client.table("secrets").delete().lt("expires_at", now_utc).execute()
            
            count = len(result.data) if result.data else 0
            logger.info(f"🧹 Limpieza completada: {count} secretos expirados eliminados")
            return count
        except Exception as e:
            logger.error(f"❌ Error al purgar secretos expirados: {e}")
            raise


# Instancia global del servicio de base de datos
database_service = DatabaseService()
