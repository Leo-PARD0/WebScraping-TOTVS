"""
Módulo: relatorio
Abre o menu de relatórios no sistema e executa submódulos.
"""

from pathlib import Path
import importlib
from typing import List, Optional

from core import utils
from core._ui import escolher_modulo_no_navegador, toast
from modulos.cadastro_produtos._navigate import abrir_menu_principal, _clicar_item_menu_por_href

SUBMOD_DIR = Path(__file__).parent / "submods"

def _listar_submodulos() -> List[str]:
    SUBMOD_DIR.mkdir(parents=True, exist_ok=True)
    mods: List[str] = []
    # Arquivos .py (exceto __init__)
    for p in SUBMOD_DIR.glob("*.py"):
        name = p.stem
        if name.startswith("_") or name in ("__init__",):
            continue
        mods.append(name)
    # Pastas com __init__.py (pacotes)
    for p in SUBMOD_DIR.iterdir():
        if p.is_dir() and (p / "__init__.py").exists():
            mods.append(p.name)
    return sorted(mods)

def _escolher_submodulo(driver, mods: List[str], preferido: Optional[str] = None) -> Optional[str]:
    default = preferido if (preferido in mods) else (mods[0] if mods else None)
    return escolher_modulo_no_navegador(driver, mods, default)

def _importar_submodulo(nome: str):
    return importlib.import_module(f".submods.{nome}", package=__package__ or "modulos.relatorio")

def executar(driver, sub_name: Optional[str] = None, **kwargs):
    utils.log.info("Abrindo menu principal (relatório)...")
    abrir_menu_principal(driver)
    utils.log.info("Clicando no item de menu Relatório...")
    _clicar_item_menu_por_href(driver, href="/Relatorios/Relatorio")
    utils.log.info("Menu de relatório aberto com sucesso!")

    # Descobre submódulos
    mods = _listar_submodulos()
    utils.log.info(f"DEBUG: Submódulos encontrados: {mods}")
    if not mods:
        raise RuntimeError("Nenhum submódulo encontrado em 'relatorio/submods/'.")

    # Suporte a sub-submódulo: --sub giro.teste
    submod = None
    subsubmod = None
    utils.log.info(f"DEBUG: sub_name recebido: {sub_name}")
    if sub_name and '.' in sub_name:
        submod, subsubmod = sub_name.split('.', 1)
        utils.log.info(f"DEBUG: submod: {submod}, subsubmod: {subsubmod}")
    elif sub_name:
        submod = sub_name
        utils.log.info(f"DEBUG: submod: {submod}")

    # Só valida o submódulo (primeiro nível)
    if submod:
        nome = submod
        utils.log.info(f"DEBUG: Validando submódulo '{nome}' em {mods}")
        if nome not in mods:
            raise RuntimeError(f"Submódulo '{nome}' não existe em 'relatorio/submods/'.")
    else:
        nome = _escolher_submodulo(driver, mods)

    if not nome:
        toast(driver, "Execução cancelada.", 2000)
        return

    # Importa e executa o submódulo de primeiro nível
    utils.log.info(f"DEBUG: Importando submódulo '{nome}'")
    mod = _importar_submodulo(nome)
    if not hasattr(mod, "executar"):
        raise RuntimeError(f"O submódulo '{nome}' precisa expor executar(driver).")

    toast(driver, f"Executando submódulo: {nome}…", 1800)
    # Passe subsubmod para o submódulo, se houver
    if subsubmod:
        utils.log.info(f"DEBUG: Chamando executar de '{nome}' com sub_name='{subsubmod}'")
        mod.executar(driver, sub_name=subsubmod, **kwargs)
    else:
        utils.log.info(f"DEBUG: Chamando executar de '{nome}' sem subsubmod")
        mod.executar(driver, **kwargs)
    toast(driver, f"Submódulo '{nome}' finalizado.", 2200)