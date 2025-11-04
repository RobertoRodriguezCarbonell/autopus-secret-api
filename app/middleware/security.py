"""
Middleware de seguridad para la API
- Rate limiting
- Request validation
- Security headers
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

from app.utils.datetime_utils import now_spain

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para limitar la cantidad de requests por IP
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = now_spain()
    
    def _cleanup_old_requests(self):
        """
        Limpiar registros antiguos para evitar memory leak
        """
        now = now_spain()
        if now - self.last_cleanup > self.cleanup_interval:
            cutoff = now - timedelta(minutes=1)
            for ip in list(self.request_counts.keys()):
                self.request_counts[ip] = [
                    timestamp for timestamp in self.request_counts[ip]
                    if timestamp > cutoff
                ]
                if not self.request_counts[ip]:
                    del self.request_counts[ip]
            self.last_cleanup = now
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesar request y aplicar rate limiting
        """
        # Obtener IP del cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Endpoints que no requieren rate limiting estricto
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/", "/health"]:
            return await call_next(request)
        
        # Verificar rate limit
        now = now_spain()
        cutoff = now - timedelta(minutes=1)
        
        # Limpiar requests antiguos de esta IP
        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if timestamp > cutoff
        ]
        
        # Verificar si excede el límite
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            logger.warning(f"⚠️ Rate limit excedido para IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Demasiadas solicitudes. Por favor, intente más tarde.",
                    "retry_after": 60
                }
            )
        
        # Registrar request
        self.request_counts[client_ip].append(now)
        
        # Cleanup periódico
        self._cleanup_old_requests()
        
        # Procesar request
        response = await call_next(request)
        
        # Agregar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.request_counts[client_ip])
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para agregar headers de seguridad
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy - Permitir recursos de Swagger UI y FastAPI docs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https://fastapi.tiangolo.com",
            "font-src 'self' https://cdn.jsdelivr.net",
            "connect-src 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        return response


def validate_content_length(max_size: int = 10 * 1024 * 1024):  # 10MB por defecto
    """
    Dependency para validar tamaño de request body
    """
    async def validator(request: Request):
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body demasiado grande. Máximo: {max_size} bytes"
                )
        return True
    return validator
