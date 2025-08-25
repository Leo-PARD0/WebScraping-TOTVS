# `core/browser.py` — Guia de uso

Este documento explica o papel do arquivo `core/browser.py` no projeto WebScraping-TOTVS, suas responsabilidades e a implementação recomendada.

---

## 1) Objetivo do `browser.py`

O arquivo `browser.py` é responsável por **criar e configurar o WebDriver** usado em todas as automações.  
Ele centraliza a lógica de inicialização do navegador (Chrome) para que o restante do projeto apenas utilize o `driver` já pronto.

---

## 2) Responsabilidades principais

- **Construção do driver** (`build_driver`): cria a instância do ChromeDriver.  
- **Configuração de opções**: headless, user profile, flags de desempenho e segurança.  
- **Gerenciamento de timeouts**: `page_load_timeout` e `implicitly_wait`.  
- **Integração opcional com webdriver-manager**: baixa o binário automaticamente caso não esteja no PATH.

---

## 3) Boas práticas aplicadas

- **Headless opcional**: configurável via variável de ambiente (`HEADLESS=true`).  
- **Perfis do Chrome**: permite reaproveitar cookies e sessões (`CHROME_USER_DATA_DIR`).  
- **Desabilitar automação visível**: `--disable-blink-features=AutomationControlled`.  
- **Timeouts claros**: `page_load_timeout` centralizado e `implicit wait` zerado (usar sempre `WebDriverWait`).

---

## 4) Estrutura recomendada

```python
"""Criação e configuração do WebDriver para WebScraping-TOTVS."""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

log = logging.getLogger("browser")


# Tenta usar webdriver-manager se disponível
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False


def build_driver(cfg):
    """Cria e retorna um driver Chrome configurado conforme cfg."""
    opts = Options()

    # Headless
    if cfg.headless:
        opts.add_argument("--headless=new")

    # User profile (opcional)
    if cfg.user_data_dir:
        opts.add_argument(f"--user-data-dir={cfg.user_data_dir}")

    # Configurações úteis
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-blink-features=AutomationControlled")


    # Criação do driver
    if USE_WDM:
        service = Service(ChromeDriverManager().install())
    else:
        service = Service()  # espera chromedriver no PATH

    driver = webdriver.Chrome(service=service, options=opts)

    # Timeouts
    driver.set_page_load_timeout(cfg.page_load_timeout)
    driver.implicitly_wait(0)  # sempre usar WebDriverWait

    log.info("Driver Chrome inicializado (headless=%s).", cfg.headless)
    return driver
```

---

## 5) Como usar no `launcher.py`

```python
from core.browser import build_driver
from core.auth import login

cfg = get_config()
driver = build_driver(cfg)
login(driver, cfg)
```

---

## 6) Erros comuns

- **Driver não encontrado**: se `webdriver-manager` não estiver instalado e o `chromedriver` não estiver no PATH.  
- **Versão incompatível**: quando o Chrome instalado e o `chromedriver` divergem → usar `webdriver-manager` resolve.  
- **Timeout ao carregar página**: ajustar `cfg.page_load_timeout` no `.env`.  
- **Headless falhando em sites modernos**: usar `--headless=new` (Selenium 4.8+) como já configurado.

---

## 7) TL;DR

- `browser.py` cria e configura o driver Chrome.  
- Usa **headless**, **user profile** e **flags extras** para estabilidade.  
- Integra com **webdriver-manager** (se instalado).  
- Sempre retorna um `driver` pronto para uso no `launcher.py` e módulos.

