# mcp/clients/__init__.py
"""Clientes HTTP para APIs externas."""

from .brasilapi_client import brasilapi_client
from .receitaws_client import receitaws_client
from .viacep_client import viacep_client
from .rag_client import rag_client

__all__ = [
    "brasilapi_client",
    "receitaws_client",
    "viacep_client",
    "rag_client"
]