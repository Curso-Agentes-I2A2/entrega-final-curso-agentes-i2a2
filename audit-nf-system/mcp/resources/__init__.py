# mcp/resources/__init__.py
"""Recursos MCP (dados contextuais)."""

from . import invoice_resource
from .invoice_resource import InvoiceResource

# __all__ = ["invoice_resource", "supplier_resource"]
__all__ = ["invoice_resource"]