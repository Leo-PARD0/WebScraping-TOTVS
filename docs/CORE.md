# `core` — Guia de uso

## 1) Objetivo da pasta
A pasta **`core/`** contém o **núcleo do WebScraping-TOTVS**.  
Aqui ficam todos os componentes essenciais que dão suporte aos módulos de automação:

- Criação e configuração do **WebDriver**  
- Fluxo de **login** e **seleção de domínio**  
- **Launcher** (ponto de entrada)  
- **Utilitários** (funções auxiliares)  
- **Seletores centralizados** (`locators.yaml`)  

O `core/` é a fundação: os módulos em `modulos/` dependem dele para funcionar.

---

## 2) Estrutura do diretório

```
core/
├─ __init__.py       # Marca a pasta como pacote Python
├─ launcher.py       # Ponto de entrada do sistema
├─ browser.py        # Criação e configuração do WebDriver
├─ auth.py           # Autenticação e seleção de domínio
├─ utils.py          # Funções auxiliares
└─ locators.yaml     # Seletores CSS/XPath centralizados
```

---

## 3) Descrição de cada arquivo

- **`__init__.py`**  
  - Marca `core/` como pacote Python.  
  - Mantido mínimo, apenas docstring.  

- **`launcher.py`**  
  - Ponto de entrada do projeto.  
  - Orquestra o fluxo: carrega configs, cria driver, faz login, seleciona domínio e executa módulos.  
  - Possui fallback para funcionar tanto com `python -m core.launcher` quanto com `python core/launcher.py`.  

- **`browser.py`**  
  - Cria o ChromeDriver com opções configuráveis.  
  - Suporta headless, user data dir e webdriver-manager.  
  - Define timeouts globais.  

- **`auth.py`**  
  - Faz login no TOTVS com credenciais.  
  - Espera tanto pós-login quanto tela de domínio.  
  - Seleciona domínio se necessário.  
  - Gera logs e screenshots em falhas.  

- **`utils.py`**  
  - Funções auxiliares.  
  - `screenshot()` → salva print em `artifacts/`.  
  - `load_locators()` → lê seletores do `locators.yaml`.  
  - `listar_modulos()` e `escolher_modulo()` → integração com `launcher.py`.  

- **`locators.yaml`**  
  - Centraliza todos os seletores CSS/XPath.  
  - Organizado por seções (`login:`, `dominio:`, etc.).  
  - Fácil manutenção quando o HTML do TOTVS muda.  

---

## 4) Fluxo de execução do `core`

1. `launcher.py` chama `get_config()` → pega credenciais.  
2. `browser.py` cria o driver.  
3. `auth.py` faz login e seleciona domínio.  
4. `utils.py` lista módulos.  
5. `launcher.py` executa o módulo escolhido.  
6. `utils.py` salva screenshots e logs se houver falhas.  

---

## 5) Boas práticas

- Sempre rodar da raiz com:
  ```bash
  python -m core.launcher
  ```
- Manter `locators.yaml` atualizado com os seletores reais do TOTVS.  
- Não colocar lógica complexa em `__init__.py`.  
- Usar `utils.py` para tudo que for função auxiliar.  
- Nunca versionar `.env` com credenciais (já está no `.gitignore`).  

---

## 6) TL;DR

- `core/` = **coração do projeto**.  
- Define login, browser, utilitários e ponto de entrada.  
- É o alicerce que permite que os módulos em `modulos/` funcionem.  
