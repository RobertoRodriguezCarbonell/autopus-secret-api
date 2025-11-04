"""
Script para probar los endpoints de la API Autopus Secret
Ejecutar con el servidor en funcionamiento
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_create_secret_simple():
    """Test 1: Crear un secreto simple sin passphrase"""
    print_separator("TEST 1: Crear secreto simple")
    
    payload = {
        "content": "Esta es una contraseña super secreta: P@ssw0rd123!",
        "ttl_minutes": 60  # 1 hora
    }
    
    response = requests.post(f"{BASE_URL}/api/secret", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_create_secret_with_passphrase():
    """Test 2: Crear un secreto con passphrase"""
    print_separator("TEST 2: Crear secreto con passphrase")
    
    payload = {
        "content": "API Key super sensible: sk-1234567890abcdef",
        "ttl_minutes": 1440,  # 24 horas
        "passphrase": "mi-passphrase-secreta"
    }
    
    response = requests.post(f"{BASE_URL}/api/secret", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_verify_passphrase(token, correct_passphrase):
    """Test 3: Verificar passphrase"""
    print_separator("TEST 3: Verificar passphrase")
    
    # Intentar con passphrase incorrecta
    print("3.1 - Passphrase incorrecta:")
    payload = {
        "token": token,
        "passphrase": "passphrase-incorrecta"
    }
    response = requests.post(f"{BASE_URL}/api/secret/verify", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Intentar con passphrase correcta
    print("\n3.2 - Passphrase correcta:")
    payload = {
        "token": token,
        "passphrase": correct_passphrase
    }
    response = requests.post(f"{BASE_URL}/api/secret/verify", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

def test_read_secret(token, passphrase=None):
    """Test 4: Leer un secreto"""
    print_separator(f"TEST 4: Leer secreto (token: {token[:10]}...)")
    
    params = {}
    if passphrase:
        params["passphrase"] = passphrase
    
    response = requests.get(f"{BASE_URL}/api/secret/{token}", params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_read_secret_twice(token):
    """Test 5: Intentar leer un secreto dos veces (debe fallar)"""
    print_separator("TEST 5: Intentar leer secreto ya consumido")
    
    response = requests.get(f"{BASE_URL}/api/secret/{token}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

def test_delete_secret():
    """Test 6: Eliminar un secreto manualmente"""
    print_separator("TEST 6: Eliminar secreto manualmente")
    
    # Primero crear un secreto
    payload = {
        "content": "Secreto para eliminar",
        "ttl_minutes": 60
    }
    create_response = requests.post(f"{BASE_URL}/api/secret", json=payload)
    token = create_response.json()["token"]
    print(f"Secreto creado con token: {token[:10]}...")
    
    # Ahora eliminarlo
    print("\nEliminando secreto...")
    delete_response = requests.delete(f"{BASE_URL}/api/secret/{token}/delete")
    print(f"Status Code: {delete_response.status_code}")
    print(f"Response:\n{json.dumps(delete_response.json(), indent=2)}")
    
    # Intentar leerlo (debe fallar)
    print("\nIntentando leer secreto eliminado...")
    read_response = requests.get(f"{BASE_URL}/api/secret/{token}")
    print(f"Status Code: {read_response.status_code}")
    print(f"Response:\n{json.dumps(read_response.json(), indent=2)}")

def test_invalid_token():
    """Test 7: Intentar leer con token inválido"""
    print_separator("TEST 7: Token inválido")
    
    response = requests.get(f"{BASE_URL}/api/secret/token-que-no-existe-123")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

def main():
    print("\n" + "🔒 AUTOPUS SECRET API - PRUEBAS DE ENDPOINTS" + "\n")
    print(f"Servidor: {BASE_URL}")
    print("="*60)
    
    try:
        # Test 1: Crear secreto simple
        secret1 = test_create_secret_simple()
        token_simple = secret1["token"]
        
        time.sleep(1)
        
        # Test 2: Crear secreto con passphrase
        secret2 = test_create_secret_with_passphrase()
        token_protected = secret2["token"]
        
        time.sleep(1)
        
        # Test 3: Verificar passphrase
        test_verify_passphrase(token_protected, "mi-passphrase-secreta")
        
        time.sleep(1)
        
        # Test 4: Leer secreto simple (primera vez - debe funcionar)
        test_read_secret(token_simple)
        
        time.sleep(1)
        
        # Test 5: Intentar leer el mismo secreto (segunda vez - debe fallar)
        test_read_secret_twice(token_simple)
        
        time.sleep(1)
        
        # Test 6: Eliminar secreto manualmente
        test_delete_secret()
        
        time.sleep(1)
        
        # Test 7: Token inválido
        test_invalid_token()
        
        time.sleep(1)
        
        # Test 8: Leer secreto protegido con passphrase
        print_separator("TEST 8: Leer secreto protegido")
        print("8.1 - Sin passphrase (debe fallar):")
        response = requests.get(f"{BASE_URL}/api/secret/{token_protected}")
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        print("\n8.2 - Con passphrase correcta:")
        test_read_secret(token_protected, "mi-passphrase-secreta")
        
        print_separator("✅ PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
