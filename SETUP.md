# 🚀 Guía de Configuración Inicial

Esta guía te ayudará a poner en marcha el proyecto por primera vez.

## Paso 1: Instalar Dependencias ✅ (Completado)

La estructura del proyecto ya está creada. Ahora necesitas instalar las dependencias.

## Paso 2: Instalar Paquetes de Python

Asegúrate de tener Python 3.9+ instalado:

```bash
python --version
```

Crea y activa un entorno virtual:

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Linux/Mac
source venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Paso 3: Configurar Variables de Entorno

1. **Copia el archivo de ejemplo:**
   ```bash
   copy .env.example .env
   ```

2. **Genera las claves necesarias:**

   **Para ENCRYPTION_KEY (Fernet):**
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
   
   **Para API_KEY_ADMIN:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Edita el archivo `.env`** con tus valores:
   - Agrega las claves generadas
   - Configura SUPABASE_URL y SUPABASE_KEY (los obtendrás en el siguiente paso)

## Paso 4: Configurar Supabase

### 4.1 Crear Proyecto en Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Crea una cuenta o inicia sesión
3. Crea un nuevo proyecto:
   - **Nombre**: `autopus-secret-api` (o el que prefieras)
   - **Contraseña de base de datos**: Guárdala en un lugar seguro
   - **Región**: Elige la más cercana a ti

4. Espera a que el proyecto se inicialice (2-3 minutos)

### 4.2 Obtener Credenciales

1. En el dashboard de tu proyecto, ve a **Settings** → **API**
2. Copia los siguientes valores a tu archivo `.env`:
   - **URL**: `SUPABASE_URL`
   - **anon/public key**: `SUPABASE_KEY`

### 4.3 Crear Tabla de Secretos

En el **Paso 2** del plan de trabajo crearemos el esquema completo de la base de datos con SQL.

## Paso 5: Verificar Instalación

Una vez instaladas las dependencias y configurado el `.env`, puedes verificar que todo funciona:

```bash
python app/main.py
```

Deberías ver:
```
🚀 Iniciando Autopus Secret API...
📍 Entorno: development
🔒 Cifrado: Habilitado
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Abre tu navegador en:
- **Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/

## ⚠️ Problemas Comunes

### Error: "No se ha podido resolver la importación"

Este error es normal antes de instalar las dependencias. Ejecuta:
```bash
pip install -r requirements.txt
```

### Error: "ValidationError" al iniciar

Falta configurar las variables de entorno. Asegúrate de:
1. Haber copiado `.env.example` a `.env`
2. Haber completado todas las variables requeridas

### Error: "Invalid encryption key"

La `ENCRYPTION_KEY` debe ser una clave Fernet válida. Genera una nueva con:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## ✅ Checklist de Configuración

- [ ] Python 3.9+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `.env` creado y configurado
- [ ] `ENCRYPTION_KEY` generada
- [ ] `API_KEY_ADMIN` generada
- [ ] Proyecto Supabase creado
- [ ] `SUPABASE_URL` y `SUPABASE_KEY` configuradas
- [ ] Servidor FastAPI arranca sin errores

## 🎯 Siguiente Paso

Una vez completado esto, estarás listo para el **Paso 2: Configuración de Supabase**, donde crearemos el esquema de la base de datos y configuraremos las políticas de seguridad.
