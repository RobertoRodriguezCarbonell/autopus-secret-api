"""
Script simple para probar la API con requests
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("🔒 AUTOPUS SECRET API - PRUEBAS SIMPLES\n")

# Test 1: Crear secreto simple
print("=" * 60)
print("TEST 1: Crear secreto simple")
print("=" * 60)
payload = {
    "content": "Mi contraseña super secreta: P@ssw0rd123!",
    "ttl_minutes": 60
}
response = requests.post(f"{BASE_URL}/api/secret", json=payload)
print(f"Status: {response.status_code}")
result1 = response.json()
print(json.dumps(result1, indent=2))
token1 = result1.get("token")

print("\n" + "=" * 60)
print("TEST 2: Crear secreto con passphrase")
print("=" * 60)
payload = {
    "content": "API Key: sk-1234567890abcdef",
    "ttl_minutes": 1440,
    "passphrase": "mi-clave-secreta"
}
response = requests.post(f"{BASE_URL}/api/secret", json=payload)
print(f"Status: {response.status_code}")
result2 = response.json()
print(json.dumps(result2, indent=2))
token2 = result2.get("token")

print("\n" + "=" * 60)
print("TEST 3: Leer secreto simple (primera vez - OK)")
print("=" * 60)
response = requests.get(f"{BASE_URL}/api/secret/{token1}")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("TEST 4: Leer secreto simple (segunda vez - DEBE FALLAR)")
print("=" * 60)
response = requests.get(f"{BASE_URL}/api/secret/{token1}")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("TEST 5: Verificar passphrase incorrecta")
print("=" * 60)
payload = {"token": token2, "passphrase": "clave-incorrecta"}
response = requests.post(f"{BASE_URL}/api/secret/verify", json=payload)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("TEST 6: Verificar passphrase correcta")
print("=" * 60)
payload = {"token": token2, "passphrase": "mi-clave-secreta"}
response = requests.post(f"{BASE_URL}/api/secret/verify", json=payload)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("TEST 7: Leer secreto protegido SIN passphrase (DEBE FALLAR)")
print("=" * 60)
response = requests.get(f"{BASE_URL}/api/secret/{token2}")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("TEST 8: Leer secreto protegido CON passphrase correcta")
print("=" * 60)
response = requests.get(f"{BASE_URL}/api/secret/{token2}", params={"passphrase": "mi-clave-secreta"})
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("TEST 9: Crear y eliminar secreto manualmente")
print("=" * 60)
payload = {"content": "Secreto para eliminar", "ttl_minutes": 60}
response = requests.post(f"{BASE_URL}/api/secret", json=payload)
token3 = response.json().get("token")
print(f"Creado: {token3[:20]}...")

response = requests.delete(f"{BASE_URL}/api/secret/{token3}/delete")
print(f"Eliminado - Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("TEST 10: Intentar leer secreto eliminado (DEBE FALLAR)")
print("=" * 60)
response = requests.get(f"{BASE_URL}/api/secret/{token3}")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n✅ PRUEBAS COMPLETADAS")
