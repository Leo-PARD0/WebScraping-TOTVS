"""Funções utilitárias do WebScraping-TOTVS."""

from __future__ import annotations

import csv
import json
import importlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import yaml

log = logging.getLogger("utils")

# Diretórios-base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
MOD_DIR = BASE_DIR / "modulos"
ARTIFACTS = BASE_DIR / "artifacts"
LOCATORS_FILE = BASE_DIR / "core" / "locators.yaml"

# Garante a pasta artifacts/
ARTIFACTS.mkdir(exist_ok=True, parents=True)


# ============================
# Captura de evidências
# ============================
def screenshot(driver, name_prefix: str) -> Path:
    """
    Salva screenshot da tela atual em artifacts/ com timestamp.
    Retorna o Path do arquivo salvo.
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = ARTIFACTS / f"{name_prefix}_{ts}.png"
    driver.save_screenshot(str(path))
    log.info("Screenshot salvo em %s", path)
    return path


# ============================
# Leitura de seletores (YAML)
# ============================
def load_locators(section: str) -> dict:
    """
    Carrega os seletores de uma seção do locators.yaml.
    Ex.: load_locators("login") -> dict com chaves/seletores da seção.
    """
    try:
        with open(LOCATORS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get(section, {})
    except FileNotFoundError:
        log.error("Arquivo locators.yaml não encontrado em %s", LOCATORS_FILE)
        return {}
    except Exception as e:
        log.error("Erro ao carregar locators.yaml: %s", e)
        return {}


# ============================
# Descoberta/Seleção de módulos
# ============================

log = logging.getLogger("utils")
BASE_DIR = Path(__file__).resolve().parents[1]
MOD_DIR = BASE_DIR / "modulos"

def _importar_executar(mod_qualname: str) -> Optional[Callable]:
    """
    Tenta importar `mod_qualname` e retornar a função pública `executar`.
    Ex.: "modulos.cadastro_produtos" ou "modulos.teste"
    """
    try:
        mod = importlib.import_module(mod_qualname)
        func = getattr(mod, "executar", None)
        return func if callable(func) else None
    except Exception as e:
        log.warning("Falha importando %s: %s", mod_qualname, e)
        return None

def listar_modulos() -> list[tuple[str, Callable]]:
    """
    Lista módulos de alto nível em `modulos/`, aceitando:
      - arquivos .py que exponham executar()
      - pacotes (pastas com __init__.py) que reexportem executar()
    Retorna lista: [(nome_curto, func_executar), ...]
    """
    mods: list[tuple[str, Callable]] = []

    # 1) Arquivos .py
    for p in sorted(MOD_DIR.glob("*.py")):
        if p.name.startswith("_"):
            continue
        qual = f"modulos.{p.stem}"
        func = _importar_executar(qual)
        if func:
            mods.append((p.stem, func))

    # 2) Pacotes (pastas com __init__.py)
    for d in sorted([x for x in MOD_DIR.iterdir() if x.is_dir()]):
        if (d / "__init__.py").exists():
            qual = f"modulos.{d.name}"
            func = _importar_executar(qual)
            if func:
                mods.append((d.name, func))

    return mods

def escolher_modulo(mods: list[tuple[str, Callable]]):
    """
    Se houver só 1 módulo, seleciona automaticamente (sem prompt).
    Caso contrário, mostra um menu no console.
    """
    if not mods:
        log.error("Nenhum módulo válido encontrado em %s", MOD_DIR)
        return None

    if len(mods) == 1:
        name, func = mods[0]
        log.info("Selecionando módulo único automaticamente: %s", name)
        return mods[0]

    print("\nMódulos disponíveis:")
    for i, (name, _) in enumerate(mods, 1):
        print(f" {i}. {name}")

    while True:
        sel = input("Escolha um módulo (número): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(mods):
            return mods[int(sel) - 1]
        print("Opção inválida.")


# ============================
# Exportação de dados
# ============================
def _ensure_output_dir() -> Path:
    """
    Garante e retorna a pasta artifacts/output.
    """
    output_dir = ARTIFACTS / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def salvar_csv(nome: str, dados: list[dict], delimiter: str = ";") -> Path:
    """
    Salva lista de dicts em CSV dentro de artifacts/output/.

    Parâmetros:
      - nome: base do nome do arquivo (sem extensão), ex.: "aliquotas"
      - dados: lista de dicionários com as mesmas chaves
      - delimiter: delimitador do CSV (padrão: ';')

    Retorna:
      - Path do arquivo salvo

    Levanta:
      - ValueError se 'dados' estiver vazio
    """
    if not dados:
        raise ValueError("Nenhum dado para salvar.")

    output_dir = _ensure_output_dir()
    caminho = output_dir / f"{nome}.csv"

    with caminho.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(dados[0].keys()), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(dados)

    log.info("CSV salvo em %s (linhas: %d)", caminho, len(dados))
    return caminho


def salvar_json(nome: str, dados: list[dict], indent: int = 2) -> Path:
    """
    Salva lista de dicts em JSON dentro de artifacts/output/.

    Parâmetros:
      - nome: base do nome do arquivo (sem extensão), ex.: "aliquotas"
      - dados: lista de dicionários
      - indent: indentação do JSON (padrão: 2)

    Retorna:
      - Path do arquivo salvo
    """
    output_dir = _ensure_output_dir()
    caminho = output_dir / f"{nome}.json"

    with caminho.open("w", encoding="utf-8") as f:
        json.dump(dados, f, indent=indent, ensure_ascii=False)

    log.info("JSON salvo em %s (linhas: %d)", caminho, len(dados))
    return caminho


__all__ = [
    "BASE_DIR",
    "MOD_DIR",
    "ARTIFACTS",
    "LOCATORS_FILE",
    "screenshot",
    "load_locators",
    "listar_modulos",
    "escolher_modulo",
    "salvar_csv",
    "salvar_json",
]
