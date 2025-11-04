@echo off
echo.
echo ========================================
echo   AUTOPUS SECRET API - PRUEBAS
echo ========================================
echo.
echo Probando endpoint: POST /api/secret (crear secreto simple)
curl -X POST "http://localhost:8000/api/secret" -H "Content-Type: application/json" -d "{\"content\":\"Mi password super secreto: P@ssw0rd123!\",\"ttl_minutes\":60}"

echo.
echo.
echo Probando endpoint: POST /api/secret (crear secreto con passphrase)
curl -X POST "http://localhost:8000/api/secret" -H "Content-Type: application/json" -d "{\"content\":\"API Key: sk-1234567890abcdef\",\"ttl_minutes\":1440,\"passphrase\":\"mi-clave-secreta\"}"

echo.
echo.
echo ========================================
echo   PRUEBAS COMPLETADAS
echo ========================================
echo.
echo Puedes probar mas endpoints en: http://localhost:8000/docs
echo.
