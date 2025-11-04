"""
Tests unitarios para generador de tokens
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.utils.token_generator import generate_token, generate_unique_token


def test_generate_token_length():
    """Test: Token generado tiene la longitud esperada"""
    token = generate_token()
    
    # token_urlsafe(48) genera ~64 caracteres
    assert len(token) >= 60
    assert len(token) <= 70


def test_generate_token_uniqueness():
    """Test: Tokens generados son únicos"""
    tokens = set()
    
    for _ in range(100):
        token = generate_token()
        assert token not in tokens
        tokens.add(token)


def test_generate_token_format():
    """Test: Token solo contiene caracteres URL-safe"""
    token = generate_token()
    
    # URL-safe: letras, números, guiones, guiones bajos
    import re
    assert re.match(r'^[A-Za-z0-9_-]+$', token)


@pytest.mark.asyncio
async def test_generate_unique_token_no_collision():
    """Test: Generar token único cuando no hay colisión"""
    # Mock database service que siempre retorna None (no existe el token)
    mock_db_service = AsyncMock()
    mock_db_service.get_secret_by_token = AsyncMock(return_value=None)
    
    token = await generate_unique_token(mock_db_service)
    
    assert token is not None
    assert len(token) >= 60
    mock_db_service.get_secret_by_token.assert_called_once()


@pytest.mark.asyncio
async def test_generate_unique_token_with_collision():
    """Test: Generar token único cuando hay colisión (primer intento existe)"""
    # Mock database service que retorna un secreto en el primer llamado, None en el segundo
    mock_db_service = AsyncMock()
    mock_db_service.get_secret_by_token = AsyncMock(
        side_effect=[{"token": "existing"}, None]
    )
    
    token = await generate_unique_token(mock_db_service)
    
    assert token is not None
    # Debe haber intentado dos veces
    assert mock_db_service.get_secret_by_token.call_count == 2


@pytest.mark.asyncio
async def test_generate_unique_token_max_retries():
    """Test: Lanzar excepción después de max intentos"""
    # Mock database service que siempre retorna un secreto existente
    mock_db_service = AsyncMock()
    mock_db_service.get_secret_by_token = AsyncMock(
        return_value={"token": "existing"}
    )
    
    with pytest.raises(RuntimeError, match="No se pudo generar un token único"):
        await generate_unique_token(mock_db_service, max_attempts=5)
    
    # Debe haber intentado 5 veces
    assert mock_db_service.get_secret_by_token.call_count == 5
