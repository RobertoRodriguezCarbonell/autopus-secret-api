-- =====================================================
-- AUTOPUS SECRET API - ESQUEMA DE BASE DE DATOS
-- =====================================================
-- Fecha de creación: 2025-11-04
-- Base de datos: Supabase PostgreSQL
-- Descripción: Tabla para almacenar secretos cifrados con caducidad automática
-- =====================================================

-- Eliminar tabla si existe (solo para desarrollo)
-- DROP TABLE IF EXISTS secrets CASCADE;

-- Crear tabla secrets
CREATE TABLE IF NOT EXISTS secrets (
    -- Identificador único del secreto
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Token único para acceder al secreto (usado en la URL)
    token VARCHAR(128) UNIQUE NOT NULL,
    
    -- Contenido del secreto cifrado con AES-256 (Fernet)
    encrypted_content TEXT NOT NULL,
    
    -- Hash bcrypt de la passphrase (opcional)
    passphrase_hash VARCHAR(255),
    
    -- Marca de tiempo de creación
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Fecha y hora de expiración del secreto
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Marca de tiempo de acceso (cuando fue leído)
    accessed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indica si el secreto fue destruido (leído o eliminado manualmente)
    is_destroyed BOOLEAN DEFAULT FALSE,
    
    -- Metadatos adicionales en formato JSON
    metadata JSONB DEFAULT '{}'::jsonb
);

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Índice en token para búsquedas rápidas por URL
CREATE INDEX IF NOT EXISTS idx_secrets_token ON secrets(token);

-- Índice en expires_at para limpieza automática de secretos expirados
CREATE INDEX IF NOT EXISTS idx_secrets_expires_at ON secrets(expires_at);

-- Índice en is_destroyed para filtrar secretos activos
CREATE INDEX IF NOT EXISTS idx_secrets_is_destroyed ON secrets(is_destroyed);

-- Índice compuesto para optimizar consultas de limpieza
-- (buscar secretos expirados que no han sido destruidos)
CREATE INDEX IF NOT EXISTS idx_secrets_cleanup 
ON secrets(expires_at, is_destroyed) 
WHERE is_destroyed = FALSE;

-- =====================================================
-- COMENTARIOS DE DOCUMENTACIÓN
-- =====================================================

COMMENT ON TABLE secrets IS 'Almacena secretos cifrados con acceso único y caducidad automática';
COMMENT ON COLUMN secrets.id IS 'Identificador único UUID del secreto';
COMMENT ON COLUMN secrets.token IS 'Token URL-safe único para acceder al secreto';
COMMENT ON COLUMN secrets.encrypted_content IS 'Contenido cifrado con Fernet (AES-256)';
COMMENT ON COLUMN secrets.passphrase_hash IS 'Hash bcrypt de la contraseña de protección (opcional)';
COMMENT ON COLUMN secrets.created_at IS 'Fecha de creación del secreto';
COMMENT ON COLUMN secrets.expires_at IS 'Fecha de expiración automática';
COMMENT ON COLUMN secrets.accessed_at IS 'Fecha en que el secreto fue accedido (primera lectura)';
COMMENT ON COLUMN secrets.is_destroyed IS 'Indica si el secreto fue destruido (true = no accesible)';
COMMENT ON COLUMN secrets.metadata IS 'Metadatos adicionales en formato JSON';

-- =====================================================
-- POLÍTICAS RLS (Row Level Security)
-- =====================================================
-- Nota: Las políticas RLS se configurarán más adelante si es necesario
-- Por ahora, la API maneja toda la autorización a nivel de aplicación

-- Habilitar RLS (descomentado cuando se necesite)
-- ALTER TABLE secrets ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- FUNCIONES AUXILIARES (FUTURAS)
-- =====================================================

-- Función para limpiar secretos expirados automáticamente
CREATE OR REPLACE FUNCTION cleanup_expired_secrets()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM secrets
    WHERE expires_at < NOW()
    AND is_destroyed = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_secrets() IS 'Elimina secretos expirados que ya fueron destruidos';

-- =====================================================
-- ESTADÍSTICAS Y VISTAS (OPCIONAL)
-- =====================================================

-- Vista para secretos activos (no destruidos y no expirados)
CREATE OR REPLACE VIEW active_secrets AS
SELECT 
    id,
    token,
    created_at,
    expires_at,
    (expires_at - NOW()) as time_remaining
FROM secrets
WHERE is_destroyed = FALSE
AND expires_at > NOW();

COMMENT ON VIEW active_secrets IS 'Vista de secretos activos (no destruidos ni expirados)';
