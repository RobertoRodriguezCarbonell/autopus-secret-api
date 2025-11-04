"""
Servicio de cifrado usando Fernet (AES-256)
"""
from cryptography.fernet import Fernet
import bcrypt
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Servicio para cifrado/descifrado de secretos y hash de passphrases
    """
    
    def __init__(self):
        """
        Inicializa el servicio con la clave de cifrado
        """
        try:
            self.fernet = Fernet(settings.encryption_key.encode())
            logger.info("✅ Servicio de cifrado inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error al inicializar servicio de cifrado: {e}")
            raise
    
    def encrypt(self, text: str) -> str:
        """
        Cifra un texto usando Fernet (AES-256)
        
        Args:
            text: Texto plano a cifrar
            
        Returns:
            Texto cifrado en base64
        """
        try:
            encrypted_bytes = self.fernet.encrypt(text.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error al cifrar: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Descifra un texto cifrado con Fernet
        
        Args:
            encrypted_text: Texto cifrado en base64
            
        Returns:
            Texto plano descifrado
        """
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error al descifrar: {e}")
            raise
    
    def hash_passphrase(self, passphrase: str) -> str:
        """
        Genera un hash bcrypt de una passphrase
        
        Args:
            passphrase: Contraseña en texto plano
            
        Returns:
            Hash bcrypt en formato string
        """
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(passphrase.encode(), salt)
            return hashed.decode()
        except Exception as e:
            logger.error(f"Error al hacer hash de passphrase: {e}")
            raise
    
    def verify_passphrase(self, passphrase: str, hashed: str) -> bool:
        """
        Verifica si una passphrase coincide con su hash
        
        Args:
            passphrase: Contraseña en texto plano
            hashed: Hash bcrypt a comparar
            
        Returns:
            True si la passphrase es correcta, False en caso contrario
        """
        try:
            return bcrypt.checkpw(passphrase.encode(), hashed.encode())
        except Exception as e:
            logger.error(f"Error al verificar passphrase: {e}")
            return False


# Instancia global del servicio de cifrado
encryption_service = EncryptionService()
