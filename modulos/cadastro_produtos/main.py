# main.py
"""
Fluxo principal do módulo 'cadastro_produtos':
1) Abre o menu do TOTVS.
2) Entra em Cadastros ▸ Produto/Serviço.
3) Lista submódulos em ./submods e executa o escolhido.
"""

from __future__ import annotations
from pathlib import Path
import sys
import importlib
from typing import List, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from ._navigate import abrir_menu_principal, ir_para_produto_servico
from core._ui import escolher_modulo_no_navegador, toast


SUBMOD_DIR = Path(__file__).parent / "submods"


def _listar_submodulos() -> List[str]:
    """Retorna a lista de submódulos (arquivos .py válidos) em ./submods."""
    SUBMOD_DIR.mkdir(parents=True, exist_ok=True)
    mods: List[str] = []
    for p in SUBMOD_DIR.glob("*.py"):
        name = p.stem
        if name.startswith("_") or name in ("__init__",):
            continue
        mods.append(name)
    return sorted(mods)

def _escolher_submodulo(driver: WebDriver, mods: List[str], preferido: str | None = None) -> Optional[str]:
    default = preferido if (preferido in mods) else ("extrair_aliquota" if "extrair_aliquota" in mods else (mods[0] if mods else None))
    return escolher_modulo_no_navegador(driver, mods, default)

def _importar_submodulo(nome: str):
    # importa como parte do pacote, p/ que os imports relativos funcionem
    return importlib.import_module(f".submods.{nome}", package=__package__ or "modulos.cadastro_produtos")


def executar(driver: WebDriver, sub_name: str | None = None) -> None:
    # 1) Navegação até a tela
    abrir_menu_principal(driver)
    ir_para_produto_servico(driver)

    # 2) Descobrir submódulos
    mods = _listar_submodulos()
    if not mods:
        raise RuntimeError("Nenhum submódulo encontrado em 'cadastro_produtos/submods/'.")

    # 3) Escolher ou forçar sub
    if sub_name:
        nome = sub_name
        if nome not in mods:
            raise RuntimeError(f"Submódulo '{nome}' não existe em 'cadastro_produtos/submods/'.")
    else:
        nome = _escolher_submodulo(driver, mods)

    if not nome:
        toast(driver, "Execução cancelada.", 2000)
        return

    # 4) Importar e rodar
    mod = _importar_submodulo(nome)
    if not hasattr(mod, "executar"):
        raise RuntimeError(f"O submódulo '{nome}.py' precisa expor executar(driver).")

    toast(driver, f"Executando submódulo: {nome}…", 1800)
    mod.executar(driver)
    toast(driver, f"Submódulo '{nome}' finalizado.", 2200)