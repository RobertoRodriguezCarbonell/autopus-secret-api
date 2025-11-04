# Script de pruebas para Autopus Secret API
# PowerShell

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  🔒 AUTOPUS SECRET API - PRUEBAS" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# Test 1: Crear secreto simple
Write-Host "TEST 1: Crear secreto simple" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
$body1 = @{
    content = "Mi password super secreto: P@ssw0rd123!"
    ttl_minutes = 60
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/api/secret" -Method Post -Body $body1 -ContentType "application/json"
    Write-Host "✅ Status: 201 Created" -ForegroundColor Green
    Write-Host "Token: $($response1.token.Substring(0,20))..." -ForegroundColor White
    Write-Host "URL: $($response1.url)" -ForegroundColor White
    Write-Host "Expira: $($response1.expires_at)" -ForegroundColor White
    $token1 = $response1.token
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 2: Crear secreto con passphrase
Write-Host "TEST 2: Crear secreto con passphrase" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
$body2 = @{
    content = "API Key: sk-1234567890abcdef"
    ttl_minutes = 1440
    passphrase = "mi-clave-secreta"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/api/secret" -Method Post -Body $body2 -ContentType "application/json"
    Write-Host "✅ Status: 201 Created" -ForegroundColor Green
    Write-Host "Token: $($response2.token.Substring(0,20))..." -ForegroundColor White
    Write-Host "URL: $($response2.url)" -ForegroundColor White
    Write-Host "Tiene passphrase: $($response2.has_passphrase)" -ForegroundColor White
    $token2 = $response2.token
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 3: Leer secreto simple (primera vez - debe funcionar)
Write-Host "TEST 3: Leer secreto simple (primera vez)" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
try {
    $response3 = Invoke-RestMethod -Uri "$baseUrl/api/secret/$token1" -Method Get
    Write-Host "✅ Status: 200 OK" -ForegroundColor Green
    Write-Host "Contenido revelado: $($response3.content)" -ForegroundColor Cyan
    Write-Host "Fue destruido: $($response3.is_destroyed)" -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 4: Intentar leer el mismo secreto (segunda vez - debe fallar)
Write-Host "TEST 4: Leer secreto ya consumido (debe fallar)" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
try {
    $response4 = Invoke-RestMethod -Uri "$baseUrl/api/secret/$token1" -Method Get
    Write-Host "❌ No debería haber funcionado!" -ForegroundColor Red
} catch {
    Write-Host "✅ Error esperado: El secreto ya fue accedido" -ForegroundColor Green
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 5: Verificar passphrase incorrecta
Write-Host "TEST 5: Verificar passphrase incorrecta" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
$body5 = @{
    token = $token2
    passphrase = "clave-incorrecta"
} | ConvertTo-Json

try {
    $response5 = Invoke-RestMethod -Uri "$baseUrl/api/secret/verify" -Method Post -Body $body5 -ContentType "application/json"
    Write-Host "❌ No debería haber funcionado!" -ForegroundColor Red
} catch {
    Write-Host "✅ Error esperado: Passphrase incorrecta" -ForegroundColor Green
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 6: Verificar passphrase correcta
Write-Host "TEST 6: Verificar passphrase correcta" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
$body6 = @{
    token = $token2
    passphrase = "mi-clave-secreta"
} | ConvertTo-Json

try {
    $response6 = Invoke-RestMethod -Uri "$baseUrl/api/secret/verify" -Method Post -Body $body6 -ContentType "application/json"
    Write-Host "✅ Status: 200 OK" -ForegroundColor Green
    Write-Host "Passphrase válida: $($response6.valid)" -ForegroundColor White
    Write-Host "Mensaje: $($response6.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 7: Leer secreto protegido SIN passphrase (debe fallar)
Write-Host "TEST 7: Leer secreto protegido SIN passphrase" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
try {
    $response7 = Invoke-RestMethod -Uri "$baseUrl/api/secret/$token2" -Method Get
    Write-Host "❌ No debería haber funcionado!" -ForegroundColor Red
} catch {
    Write-Host "✅ Error esperado: Falta passphrase" -ForegroundColor Green
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 8: Leer secreto protegido CON passphrase correcta
Write-Host "TEST 8: Leer secreto protegido CON passphrase" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
try {
    $response8 = Invoke-RestMethod -Uri "$baseUrl/api/secret/$token2`?passphrase=mi-clave-secreta" -Method Get
    Write-Host "✅ Status: 200 OK" -ForegroundColor Green
    Write-Host "Contenido revelado: $($response8.content)" -ForegroundColor Cyan
    Write-Host "Fue destruido: $($response8.is_destroyed)" -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 9: Crear secreto y eliminarlo manualmente
Write-Host "TEST 9: Crear y eliminar secreto manualmente" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
$body9 = @{
    content = "Secreto para eliminar"
    ttl_minutes = 60
} | ConvertTo-Json

try {
    $response9 = Invoke-RestMethod -Uri "$baseUrl/api/secret" -Method Post -Body $body9 -ContentType "application/json"
    $token3 = $response9.token
    Write-Host "Secreto creado: $($token3.Substring(0,20))..." -ForegroundColor White
    
    $response9b = Invoke-RestMethod -Uri "$baseUrl/api/secret/$token3/delete" -Method Delete
    Write-Host "✅ Secreto eliminado exitosamente" -ForegroundColor Green
    Write-Host "Mensaje: $($response9b.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 1

# Test 10: Intentar leer secreto eliminado
Write-Host "TEST 10: Leer secreto eliminado (debe fallar)" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
try {
    $response10 = Invoke-RestMethod -Uri "$baseUrl/api/secret/$token3" -Method Get
    Write-Host "❌ No debería haber funcionado!" -ForegroundColor Red
} catch {
    Write-Host "✅ Error esperado: El secreto fue destruido" -ForegroundColor Green
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  ✅ TODAS LAS PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentación interactiva: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
