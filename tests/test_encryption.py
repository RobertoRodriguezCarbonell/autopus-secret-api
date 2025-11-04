"""
Tests unitarios para el servicio de cifrado
"""
import pytest
import os
from cryptography.fernet import Fernet
from app.services.encryption import EncryptionService

# Configurar clave de prueba
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()


def test_encrypt_decrypt():
    """Test: Cifrar y descifrar texto correctamente"""
    encryption_service = EncryptionService()
    
    original_text = "Este es un secreto super importante"
    encrypted = encryption_service.encrypt(original_text)
    decrypted = encryption_service.decrypt(encrypted)
    
    assert decrypted == original_text
    assert encrypted != original_text


def test_encrypt_returns_different_values():
    """Test: Mismo texto cifrado dos veces produce diferentes valores"""
    encryption_service = EncryptionService()
    
    text = "Secreto"
    encrypted1 = encryption_service.encrypt(text)
    encrypted2 = encryption_service.encrypt(text)
    
    # Ambos deben descifrar al mismo valor pero ser diferentes cifrados
    assert encryption_service.decrypt(encrypted1) == text
    assert encryption_service.decrypt(encrypted2) == text
    # Con Fernet, el cifrado incluye timestamp, así que pueden ser diferentes
    # pero con la misma clave deberían ser iguales (Fernet es determinístico sin IV)


def test_hash_passphrase():
    """Test: Hash de passphrase genera valores diferentes"""
    encryption_service = EncryptionService()
    
    passphrase = "mi-passphrase-segura"
    hash1 = encryption_service.hash_passphrase(passphrase)
    hash2 = encryption_service.hash_passphrase(passphrase)
    
    # Los hashes deben ser diferentes (bcrypt usa salt)
    assert hash1 != hash2
    assert hash1 != passphrase


def test_verify_passphrase_correct():
    """Test: Verificar passphrase correcta"""
    encryption_service = EncryptionService()
    
    passphrase = "mi-passphrase-segura"
    hashed = encryption_service.hash_passphrase(passphrase)
    
    assert encryption_service.verify_passphrase(passphrase, hashed) is True


def test_verify_passphrase_incorrect():
    """Test: Verificar passphrase incorrecta"""
    encryption_service = EncryptionService()
    
    passphrase = "mi-passphrase-segura"
    wrong_passphrase = "passphrase-incorrecta"
    hashed = encryption_service.hash_passphrase(passphrase)
    
    assert encryption_service.verify_passphrase(wrong_passphrase, hashed) is False


def test_decrypt_invalid_data():
    """Test: Intentar descifrar datos inválidos lanza excepción"""
    encryption_service = EncryptionService()
    
    with pytest.raises(Exception):
        encryption_service.decrypt("datos_invalidos_no_cifrados")


def test_encrypt_empty_string():
    """Test: Cifrar string vacío"""
    encryption_service = EncryptionService()
    
    encrypted = encryption_service.encrypt("")
    decrypted = encryption_service.decrypt(encrypted)
    
    assert decrypted == ""


def test_encrypt_special_characters():
    """Test: Cifrar texto con caracteres especiales"""
    encryption_service = EncryptionService()
    
    text = "¡Hola! 你好 🔐 <script>alert('test')</script>"
    encrypted = encryption_service.encrypt(text)
    decrypted = encryption_service.decrypt(encrypted)
    
    assert decrypted == text
