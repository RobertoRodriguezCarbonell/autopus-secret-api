"""
Autopus Secret API - Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routers import secrets, admin

# Configurar logging
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    # Startup
    logger.info("🚀 Iniciando Autopus Secret API...")
    logger.info(f"📍 Entorno: {settings.environment}")
    logger.info(f"🔒 Cifrado: Habilitado")
    
    # Iniciar scheduler para limpieza automática
    from app.scheduler import start_scheduler
    start_scheduler()
    
    yield
    
    # Shutdown
    logger.info("🛑 Deteniendo Autopus Secret API...")
    
    # Detener scheduler
    from app.scheduler import shutdown_scheduler
    shutdown_scheduler()


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API segura para compartir secretos con caducidad automática y acceso único",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    # Configurar esquema de seguridad para Swagger
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar middlewares de seguridad
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

logger.info("🛡️ Middlewares de seguridad configurados")

# Incluir routers
app.include_router(secrets.router, prefix="/api", tags=["Secrets"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz - Información básica de la API
    """
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "online",
        "docs": "/docs",
        "environment": settings.environment
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check básico
    """
    return {
        "status": "healthy",
        "version": settings.api_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=not settings.is_production
    )
