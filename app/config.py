"""
Configuración centralizada de la aplicación usando Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno
    """
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Cifrado
    encryption_key: str
    
    # Autenticación Admin
    api_key_admin: str
    
    # General
    environment: str = "development"
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "Autopus Secret API"
    api_version: str = "0.1.0"
    
    # Límites
    max_secret_size_kb: int = 10
    min_ttl_minutes: int = 5
    max_ttl_minutes: int = 10080  # 7 días
    
    # Scheduler
    cleanup_interval_hours: int = 1
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convierte la cadena de orígenes CORS en una lista
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """
        Verifica si el entorno es producción
        """
        return self.environment.lower() == "production"
    
    @property
    def max_secret_size_bytes(self) -> int:
        """
        Convierte el límite de KB a bytes
        """
        return self.max_secret_size_kb * 1024


# Instancia global de configuración
settings = Settings()
