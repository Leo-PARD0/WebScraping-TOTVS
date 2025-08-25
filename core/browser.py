"""Criação e configuração do WebDriver para WebScraping-TOTVS."""

import logging
import os
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
