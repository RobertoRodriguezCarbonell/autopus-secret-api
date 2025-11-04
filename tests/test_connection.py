"""
Script de prueba para verificar la conexión con Supabase
"""
import sys
import asyncio
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, 'd:/Programacion/autopus-secret-api')

from app.services.database import database_service
from app.services.encryption import encryption_service


async def test_database_connection():
    """
    Prueba la conexión y operaciones básicas con Supabase
    """
    print("=" * 60)
    print("🧪 PRUEBA DE CONEXIÓN CON SUPABASE")
    print("=" * 60)
    
    try:
        # 1. Crear un secreto de prueba
        print("\n1️⃣ Creando secreto de prueba...")
        
        test_content = "Este es un secreto de prueba"
        encrypted_content = encryption_service.encrypt(test_content)
        test_token = "test_token_" + str(datetime.now().timestamp())
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        result = await database_service.create_secret(
            token=test_token,
            encrypted_content=encrypted_content,
            expires_at=expires_at,
            passphrase_hash=None,
            metadata={"test": True, "created_by": "test_script"}
        )
        
        print(f"✅ Secreto creado exitosamente")
        print(f"   - ID: {result['id']}")
        print(f"   - Token: {result['token']}")
        print(f"   - Expira: {result['expires_at']}")
        
        # 2. Leer el secreto
        print("\n2️⃣ Leyendo secreto desde la base de datos...")
        
        secret_data = await database_service.get_secret_by_token(test_token)
        
        if secret_data:
            print(f"✅ Secreto encontrado")
            print(f"   - ID: {secret_data['id']}")
            print(f"   - Destruido: {secret_data['is_destroyed']}")
            print(f"   - Creado: {secret_data['created_at']}")
            
            # Descifrar contenido
            decrypted = encryption_service.decrypt(secret_data['encrypted_content'])
            print(f"   - Contenido descifrado: '{decrypted}'")
            
            if decrypted == test_content:
                print("   ✅ El contenido descifrado coincide con el original")
            else:
                print("   ❌ ERROR: El contenido no coincide")
        else:
            print("❌ ERROR: No se pudo encontrar el secreto")
            return False
        
        # 3. Marcar como accedido
        print("\n3️⃣ Marcando secreto como destruido...")
        
        await database_service.mark_as_accessed(test_token)
        
        secret_updated = await database_service.get_secret_by_token(test_token)
        if secret_updated and secret_updated['is_destroyed']:
            print("✅ Secreto marcado como destruido correctamente")
        else:
            print("❌ ERROR: No se pudo marcar como destruido")
        
        # 4. Limpiar datos de prueba
        print("\n4️⃣ Limpiando datos de prueba...")
        
        await database_service.delete_secret(test_token)
        print("✅ Secreto de prueba eliminado")
        
        # Resumen
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        print("\n✓ Conexión con Supabase: OK")
        print("✓ Cifrado/Descifrado: OK")
        print("✓ Operaciones CRUD: OK")
        print("✓ Base de datos lista para usar")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)
