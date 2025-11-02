# """
# Middleware de logging personalizado.

# Registra requisições, respostas e métricas de performance.
# """
# from fastapi import Request, Response
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.types import ASGIApp
# import time
# import logging
# import json
# from typing import Callable

# logger = logging.getLogger(__name__)


# class LoggingMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware para logging detalhado de requisições.
    
#     Registra:
#     - Método HTTP e URL
#     - Status code da resposta
#     - Tempo de processamento
#     - IP do cliente
#     - User agent
#     - Corpo da requisição (para erros)
#     """
    
#     def __init__(self, app: ASGIApp):
#         super().__init__(app)
    
#     async def dispatch(
#         self,
#         request: Request,
#         call_next: Callable
#     ) -> Response:
#         """
#         Processa requisição e adiciona logging.
        
#         Args:
#             request: Requisição HTTP
#             call_next: Próximo handler
        
#         Returns:
#             Resposta HTTP
#         """
#         # Marca início do processamento
#         start_time = time.time()
        
#         # Extrai informações da requisição
#         method = request.method
#         url = str(request.url)
#         client_ip = request.client.host if request.client else "unknown"
#         user_agent = request.headers.get("user-agent", "unknown")
        
#         # Processa requisição
#         try:
#             response = await call_next(request)
            
#             # Calcula tempo de processamento
#             process_time = time.time() - start_time
            
#             # Log da requisição
#             log_data = {
#                 "method": method,
#                 "url": url,
#                 "status_code": response.status_code,
#                 "process_time": f"{process_time:.3f}s",
#                 "client_ip": client_ip,
#                 "user_agent": user_agent
#             }
            
#             # Log com nível apropriado
#             if response.status_code >= 500:
#                 logger.error(f"Server Error: {json.dumps(log_data)}")
#             elif response.status_code >= 400:
#                 logger.warning(f"Client Error: {json.dumps(log_data)}")
#             else:
#                 logger.info(f"Request: {json.dumps(log_data)}")
            
#             # Adiciona header com tempo de processamento
#             response.headers["X-Process-Time"] = str(process_time)
            
#             return response
            
#         except Exception as e:
#             # Calcula tempo até o erro
#             process_time = time.time() - start_time
            
#             # Log de erro
#             logger.error(
#                 f"Exception during request: {method} {url} - "
#                 f"Error: {str(e)} - "
#                 f"Time: {process_time:.3f}s - "
#                 f"Client: {client_ip}"
#             )
            
#             # Re-raise para ser tratado por outros handlers
#             raise


# class RequestIDMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware para adicionar ID único a cada requisição.
    
#     Útil para rastreamento e debugging.
#     """
    
#     async def dispatch(
#         self,
#         request: Request,
#         call_next: Callable
#     ) -> Response:
#         """
#         Adiciona request_id único.
        
#         Args:
#             request: Requisição HTTP
#             call_next: Próximo handler
        
#         Returns:
#             Resposta HTTP com header X-Request-ID
#         """
#         import uuid
        
#         # Gera ID único
#         request_id = str(uuid.uuid4())
        
#         # Adiciona ao state da request (acessível em handlers)
#         request.state.request_id = request_id
        
#         # Processa requisição
#         response = await call_next(request)
        
#         # Adiciona request_id ao header da resposta
#         response.headers["X-Request-ID"] = request_id
        
#         return response


# class RateLimitMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware simples de rate limiting.
    
#     Limita número de requisições por IP.
#     """
    
#     def __init__(self, app: ASGIApp, max_requests: int = 100, window: int = 60):
#         """
#         Inicializa rate limiter.
        
#         Args:
#             app: Aplicação ASGI
#             max_requests: Máximo de requisições permitidas
#             window: Janela de tempo em segundos
#         """
#         super().__init__(app)
#         self.max_requests = max_requests
#         self.window = window
#         self.requests = {}  # {ip: [(timestamp, ...)]}
    
#     async def dispatch(
#         self,
#         request: Request,
#         call_next: Callable
#     ) -> Response:
#         """
#         Verifica rate limit antes de processar.
        
#         Args:
#             request: Requisição HTTP
#             call_next: Próximo handler
        
#         Returns:
#             Resposta HTTP ou erro 429 se limite excedido
#         """
#         from fastapi import HTTPException, status
        
#         # Obtém IP do cliente
#         client_ip = request.client.host if request.client else "unknown"
        
#         # Ignora rate limit para IPs locais
#         if client_ip in ["127.0.0.1", "localhost"]:
#             return await call_next(request)
        
#         current_time = time.time()
        
#         # Inicializa lista de requisições para o IP
#         if client_ip not in self.requests:
#             self.requests[client_ip] = []
        
#         # Remove requisições antigas (fora da janela)
#         self.requests[client_ip] = [
#             timestamp for timestamp in self.requests[client_ip]
#             if current_time - timestamp < self.window
#         ]
        
#         # Verifica se excedeu o limite
#         if len(self.requests[client_ip]) >= self.max_requests:
#             logger.warning(
#                 f"Rate limit exceeded for IP: {client_ip} - "
#                 f"{len(self.requests[client_ip])} requests in {self.window}s"
#             )
            
#             raise HTTPException(
#                 status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#                 detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window}s"
#             )
        
#         # Adiciona requisição atual
#         self.requests[client_ip].append(current_time)
        
#         # Processa requisição
#         response = await call_next(request)
        
#         # Adiciona headers informativos
#         remaining = self.max_requests - len(self.requests[client_ip])
#         response.headers["X-RateLimit-Limit"] = str(self.max_requests)
#         response.headers["X-RateLimit-Remaining"] = str(remaining)
#         response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window))
        
#         return response