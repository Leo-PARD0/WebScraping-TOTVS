"""Funções utilitárias do WebScraping-TOTVS."""

import importlib
import logging
from datetime import datetime
from pathlib import Path
import yaml

log = logging.getLogger("utils")

BASE_DIR = Path(__file__).resolve().parents[1]
MOD_DIR = BASE_DIR / "modulos"
ARTIFACTS = BASE_DIR / "artifacts"
LOCATORS_FILE = BASE_DIR / "core" / "locators.yaml"

ARTIFACTS.mkdir(exist_ok=True, parents=True)


def screenshot(driver, name_prefix: str):
    """Salva screenshot da tela atual em artifacts/ com timestamp."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = ARTIFACTS / f"{name_prefix}_{ts}.png"
    driver.save_screenshot(str(path))
    log.info("Screenshot salvo em %s", path)
    return path


def load_locators(section: str) -> dict:
    """Carrega os seletores de uma seção do locators.yaml."""
    try:
        with open(LOCATORS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get(section, {})
    except FileNotFoundError:
        log.error("Arquivo locators.yaml não encontrado em %s", LOCATORS_FILE)
        return {}
    except Exception as e:
        log.error("Erro ao carregar locators.yaml: %s", e)
        return {}


def listar_modulos() -> list[tuple[str, callable]]:
    """Lista todos os módulos válidos (com função executar)."""
    mods = []
    for p in sorted(MOD_DIR.glob("*.py")):
        if p.name.startswith("_"):
            continue
        mod_name = f"modulos.{p.stem}"
        try:
            mod = importlib.import_module(mod_name)
            func = getattr(mod, "executar", None)
            if callable(func):
                mods.append((p.stem, func))
        except Exception as e:
            log.warning("Falha importando %s: %s", mod_name, e)
    return mods


def escolher_modulo(mods: list[tuple[str, callable]]):
    """Mostra menu interativo para escolher um módulo."""
    if not mods:
        log.error("Nenhum módulo válido encontrado em %s", MOD_DIR)
        return None

    print("\nMódulos disponíveis:")
    for i, (name, _) in enumerate(mods, 1):
        print(f" {i}. {name}")

    while True:
        sel = input("Escolha um módulo (número): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(mods):
            return mods[int(sel) - 1]
        print("Opção inválida.")
