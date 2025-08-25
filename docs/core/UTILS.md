# `core/utils.py` — Guia de uso

Este documento explica o papel do arquivo `core/utils.py` no projeto WebScraping-TOTVS, suas responsabilidades e a implementação recomendada.

---

## 1) Objetivo do `utils.py`

O `utils.py` concentra funções **auxiliares e reutilizáveis** que dão suporte ao núcleo do sistema.  
Essas funções não pertencem exclusivamente a `auth.py`, `browser.py` ou `launcher.py`, mas são necessárias em vários pontos do projeto.

---

## 2) Responsabilidades principais

- **Screenshot (`screenshot`)**: salva um print da tela em `artifacts/` em caso de falha.  
- **Carregar seletores (`load_locators`)**: lê a seção apropriada do `locators.yaml`.  
- **Listar módulos (`listar_modulos`)**: identifica todos os módulos disponíveis em `modulos/`.  
- **Escolher módulo (`escolher_modulo`)**: exibe um menu interativo no console para o usuário selecionar um módulo.  

---

## 3) Estrutura recomendada

```python
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
        if p.name.startswith("_"):  # ignora arquivos iniciados com _
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
```

---

## 4) Onde cada função é usada

- **`screenshot`** → usada em `auth.py` (falha de login) e `launcher.py` (erros gerais).  
- **`load_locators`** → usada em `auth.py` e pode ser usada por módulos de scraping.  
- **`listar_modulos`** → usada em `launcher.py` para descobrir módulos disponíveis.  
- **`escolher_modulo`** → usada em `launcher.py` para permitir ao usuário escolher qual módulo executar.  

---

## 5) Boas práticas

- Sempre salvar **screenshots com timestamp** para facilitar debug.  
- Garantir que `locators.yaml` esteja sempre sincronizado com o sistema TOTVS.  
- Evitar colocar lógica de negócio aqui → apenas utilidades genéricas.  
- Usar `log` em todas as funções para manter rastreabilidade.  

---

## 6) Erros comuns

- **Arquivo `locators.yaml` não encontrado** → verifique se ele existe em `core/`.  
- **Indentação incorreta no YAML** → YAML exige 2 espaços por nível.  
- **Módulo sem função `executar`** → será ignorado por `listar_modulos`.  
- **Loop infinito no menu** → se não digitar um número válido, o `escolher_modulo` continua perguntando.  

---

## 7) TL;DR

- `utils.py` contém funções auxiliares para screenshots, leitura de seletores e gerenciamento de módulos.  
- É chamado tanto pelo `launcher.py` quanto por `auth.py`.  
- Mantém o núcleo do projeto limpo e organizado.  

