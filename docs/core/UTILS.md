# `core/utils.py` — Guia de uso

## 1) Objetivo
Concentrar **funções utilitárias e reutilizáveis** do projeto WebScraping-TOTVS:
- Captura de evidências (screenshots)
- Leitura centralizada de seletores (YAML)
- Descoberta/seleção de módulos
- Exportação padronizada de dados (CSV/JSON)

## 2) Estrutura e constantes
- `BASE_DIR`: raiz do projeto
- `MOD_DIR`: pasta `modulos/`
- `ARTIFACTS`: pasta `artifacts/`
- `LOCATORS_FILE`: caminho de `core/locators.yaml`

As pastas necessárias são criadas automaticamente quando o módulo é importado.

## 3) Funções principais

### 3.1 Evidências
- `screenshot(driver, name_prefix) -> Path`  
  Salva um PNG com timestamp em `artifacts/`.

### 3.2 Seletores (YAML)
- `load_locators(section) -> dict`  
  Lê `core/locators.yaml` e retorna apenas a seção solicitada (ex.: `"login"`).

### 3.3 Módulos
- `listar_modulos() -> list[(nome, executar)]`  
  Varre `modulos/*.py`, importa e retorna os que expõem `executar()`.
- `escolher_modulo(mods)`  
  Menu de console para escolher um módulo (tupla retornada por `listar_modulos`).

### 3.4 Exportação de dados
- `salvar_csv(nome, dados, delimiter=';') -> Path`  
  Salva lista de dicionários em `artifacts/output/<nome>.csv`.  
  Todas as linhas devem ter as mesmas chaves.
- `salvar_json(nome, dados, indent=2) -> Path`  
  Salva lista de dicionários em `artifacts/output/<nome>.json`.

## 4) Boas práticas
- Centralize **toda exportação** (CSV/JSON/Excel futuro) aqui para evitar duplicação.
- Use `screenshot()` em pontos críticos (ex.: falhas de login, exceções inesperadas).
- Mantenha `locators.yaml` atualizado quando o HTML do TOTVS mudar.

## 5) Exemplo de uso (submódulo)
```python
from core import utils

def executar(driver):
    # ... coletar dados na tela ...
    linhas = [
        {"codigo": "123", "nome": "Produto A", "aliquota_icms": "18%"},
        {"codigo": "456", "nome": "Produto B", "aliquota_icms": "12%"},
    ]
    utils.salvar_csv("aliquotas", linhas)      # artifacts/output/aliquotas.csv
    utils.salvar_json("aliquotas", linhas)     # artifacts/output/aliquotas.json
6) TL;DR

utils.py é o hub de utilidades do projeto.

Aqui ficam evidências, seletores, descoberta de módulos e exportação padronizada.

Submódulos chamam salvar_csv/json() — sem reinventar a roda.
"""
::contentReference[oaicite:0]{index=0}
