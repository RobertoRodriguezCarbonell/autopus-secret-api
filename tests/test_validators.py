"""
Tests unitarios para validadores y utilidades
"""
import pytest
from datetime import datetime, timedelta, timezone
from app.utils.validators import (
    validate_ttl,
    calculate_expiration,
    validate_content_size,
    validate_passphrase
)


def test_validate_ttl_valid():
    """Test: TTL válido pasa la validación"""
    validate_ttl(60)  # No debe lanzar excepción
    validate_ttl(5)
    validate_ttl(10080)


def test_validate_ttl_too_small():
    """Test: TTL menor al mínimo lanza ValueError"""
    with pytest.raises(ValueError, match="mínimo permitido"):
        validate_ttl(4)


def test_validate_ttl_too_large():
    """Test: TTL mayor al máximo lanza ValueError"""
    with pytest.raises(ValueError, match="máximo permitido"):
        validate_ttl(10081)


def test_calculate_expiration():
    """Test: Calcular expiración correctamente"""
    ttl_minutes = 60
    before = datetime.now(timezone.utc)
    expiration = calculate_expiration(ttl_minutes)
    after = datetime.now(timezone.utc)
    
    # La expiración debe estar aproximadamente 60 minutos en el futuro
    expected_expiration = before + timedelta(minutes=ttl_minutes)
    
    # Permitir margen de 1 segundo
    assert abs((expiration - expected_expiration).total_seconds()) < 1


def test_validate_content_size_valid():
    """Test: Contenido de tamaño válido pasa la validación"""
    content = "Este es un secreto" * 100  # ~1.8KB
    validate_content_size(content)  # No debe lanzar excepción


def test_validate_content_size_too_large():
    """Test: Contenido demasiado grande lanza ValueError"""
    # Crear contenido mayor a 10KB
    large_content = "x" * (10 * 1024 + 1)
    
    with pytest.raises(ValueError, match="excede el tamaño máximo"):
        validate_content_size(large_content)


def test_validate_content_size_empty():
    """Test: Contenido vacío no lanza error (el error se maneja en otro lado)"""
    # El validador solo comprueba tamaño máximo, no mínimo
    validate_content_size("")  # No debería lanzar excepción


def test_validate_passphrase_valid():
    """Test: Passphrase válida pasa la validación"""
    validate_passphrase("mi-passphrase-segura")
    validate_passphrase("123456")
    validate_passphrase("a" * 100)


def test_validate_passphrase_too_short():
    """Test: Passphrase demasiado corta lanza ValueError"""
    with pytest.raises(ValueError, match="al menos 6 caracteres"):
        validate_passphrase("12345")


def test_validate_passphrase_none():
    """Test: Passphrase None no lanza excepción (es opcional)"""
    validate_passphrase(None)  # No debe lanzar excepción


def test_validate_passphrase_empty():
    """Test: Passphrase vacía lanza ValueError"""
    with pytest.raises(ValueError, match="al menos 6 caracteres"):
        validate_passphrase("")
