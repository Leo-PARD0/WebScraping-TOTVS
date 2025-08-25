# ESTRUTURA DO PROJETO — WebScraping-TOTVS

Este documento define a estrutura de pastas/arquivos do projeto, convenções e como criar tudo do zero.

> **Objetivo**: separar o _core_ (launcher, autenticação, criação do driver, utilidades) dos _módulos_ (rotinas de automação específicas), com áreas dedicadas para _artefatos_ (logs, screenshots) e _saídas_ (CSV/Excel).

---

## 🌳 Árvore de diretórios

```
WebScraping-TOTVS/
├─ core/                     # Núcleo reutilizável
│  ├─ __init__.py
│  ├─ launcher.py            # Ponto de entrada (substitui gpt_selenium.py)
│  ├─ auth.py                # Login, seleção de domínio e helpers de sessão
│  ├─ browser.py             # Criação/configuração do WebDriver
│  ├─ utils.py               # Funções utilitárias (listar módulos, screenshot, etc.)
│  └─ locators.yaml          # Seletores (CSS/XPath) centralizados
│
├─ modulos/                  # Suas automações; cada arquivo = um módulo
│  ├─ __init__.py
│  └─ exemplo_modulo.py      # Exemplo com função `executar(driver, **kwargs)`
│
├─ artifacts/                # Logs, screenshots e fontes de página para debug
├─ output/                   # Dados exportados (CSV/Excel/Parquet)
├─ docs/                     # Documentação do projeto
│  └─ ESTRUTURA.md
│
├─ .env.example              # Modelo de variáveis de ambiente
├─ .gitignore
├─ requirements.txt
├─ pyproject.toml            # (Opcional) Configuração de tooling (ruff/black/pytest)
└─ README.md
```

---

## 🧩 Funções & contratos

### Módulos (em `modulos/`)
- Cada módulo é um arquivo `snake_case.py` contendo **obrigatoriamente**:
  ```python
  def executar(driver, **kwargs):
      """Ponto de entrada do módulo."""
      ...
  ```
- O `launcher.py` descobre automaticamente os módulos válidos (os que possuem `executar`) e mostra um menu para escolher.

### Core
- `core/launcher.py`: inicializa config, cria driver, faz login/seleção de domínio e executa o módulo escolhido.
- `core/auth.py`: fluxo de autenticação e pós-login (retries + waits).
- `core/browser.py`: opções do Chrome, `Service` (com ou sem webdriver-manager), timeouts.
- `core/utils.py`: `listar_modulos()`, `screenshot()`, salvamento de `page_source`, utilidades de logging/tempo.
- `core/locators.yaml`: seletores CSS/XPath organizados por tela/etapa (mais fácil de manter).

---

## 🔐 Variáveis de ambiente (.env)

Arquivo `/.env.example` (copie para `.env` e preencha):
```
TOTVS_URL=https://sua-instancia-totvs.exemplo
TOTVS_USER=seu.usuario
TOTVS_PASS=sua.senha

# Opcional
HEADLESS=false
CHROME_USER_DATA_DIR=
```

---

## 🧪 Requisitos & execução

### Python
- Versão recomendada: **3.10+**

### Dependências (requirements.txt)
```
selenium>=4.23
python-dotenv>=1.0
webdriver-manager>=4.0
pandas>=2.2
pyyaml>=6.0
```

### Rodando
- Via módulo:
  ```bash
  python -m core.launcher
  ```
- Ou diretamente:
  ```bash
  python core/launcher.py
  ```

---

## 🧭 Convenções

- **Seletores**: priorizar IDs estáveis ou atributos `data-*`. XPath só quando necessário.
- **Espera**: usar `WebDriverWait` (evitar `time.sleep`).
- **Logs & artefatos**:
  - Logs em `artifacts/run.log`.
  - Screenshots e `page_source` salvos automaticamente em erros.
- **Saídas**: dados tabulares sempre em `output/` com timestamp no nome do arquivo.
- **Nomes de módulos**: `snake_case.py` descrevendo a ação (ex.: `exportar_produtos.py`).

---

## 📦 Arquivos mínimos (stubs)

Crie estes arquivos com o conteúdo inicial:

**`core/__init__.py`**
```python
"""Core do WebScraping-TOTVS."""
```

**`modulos/__init__.py`**
```python
"""Módulos de automação do WebScraping-TOTVS."""
```

**`modulos/exemplo_modulo.py`**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def executar(driver, **kwargs):
    wait = WebDriverWait(driver, 25)
    # TODO: sua automação aqui
    return
```

**`.env.example`**
```dotenv
TOTVS_URL=
TOTVS_USER=
TOTVS_PASS=
HEADLESS=false
CHROME_USER_DATA_DIR=
```

**`.gitignore` (trecho sugerido)**
```
# Python
__pycache__/
*.pyc

# Env
.env

# Artefatos/saídas
artifacts/
output/

# SO/IDE
.DS_Store
.vscode/
```

---

## 🛠️ Criando estrutura (comandos)

> Escolha **um** dos blocos (PowerShell **ou** bash) e rode na raiz do repositório.

### Windows (PowerShell)
```powershell
New-Item -ItemType Directory core, modulos, artifacts, output, docs
New-Item -ItemType File core/__init__.py, modulos/__init__.py, modulos/exemplo_modulo.py, .env.example, .gitignore, requirements.txt, README.md, docs/ESTRUTURA.md | Out-Null
```

### Linux/macOS (bash)
```bash
mkdir -p core modulos artifacts output docs
touch core/__init__.py modulos/__init__.py modulos/exemplo_modulo.py .env.example .gitignore requirements.txt README.md docs/ESTRUTURA.md
```

> Depois, copie o conteúdo deste arquivo para `docs/ESTRUTURA.md` (o próprio arquivo que você está lendo).

---

## ▶️ Próximos passos

1. Implementar `core/launcher.py` e `core/browser.py` (criação do driver).
2. Implementar `core/auth.py` (login + seleção de domínio) e popular `core/locators.yaml`.
3. Criar o primeiro módulo real em `modulos/` e testar o fluxo fim-a-fim.
