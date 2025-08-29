# modulos/cadastro_produtos/__init__.py
"""
Módulo de alto nível para o fluxo de Cadastro de Produtos.
Reexporta `executar(driver)` a partir de `main.py`.
"""

from .main import executar # reexporta a função principal
from core._ui import escolher_modulo_no_navegador, toast  

__all__ = ["executar"]
