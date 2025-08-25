"""Autenticação e seleção de domínio para WebScraping-TOTVS."""

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from .utils import screenshot, load_locators

log = logging.getLogger("auth")

def login(driver, cfg):
    """Realiza o login no TOTVS usando credenciais do cfg.
    Após submeter, espera EITHER: after_login OU a tela de domínio.
    """
    loc_login = load_locators("login")
    loc_dom   = load_locators("dominio")

    log.info("Acessando %s ...", cfg.url)
    driver.get(cfg.url)

    try:
        wait = WebDriverWait(driver, cfg.explicit_timeout)

        # Campos de login
        user_sel = loc_login["user"]
        pass_sel = loc_login["password"]
        submit_sel = loc_login["submit"]

        user_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, user_sel)))
        pass_el = driver.find_element(By.CSS_SELECTOR, pass_sel)

        user_el.clear()
        user_el.send_keys(cfg.user)
        pass_el.clear()
        pass_el.send_keys(cfg.password)

        driver.find_element(By.CSS_SELECTOR, submit_sel).click()

        # ---- ESPERA INTELIGENTE: pós-login OU tela de domínio ----
        conds = []
        if "after_login" in loc_login:
            conds.append(EC.presence_of_element_located((By.CSS_SELECTOR, loc_login["after_login"])))
        if "container" in loc_dom:
            conds.append(EC.presence_of_element_located((By.CSS_SELECTOR, loc_dom["container"])))

        if not conds:
            raise TimeoutException("Config de locators incompleta: defina login.after_login e/ou dominio.container")

        wait.until(EC.any_of(*conds))
        log.info("Login realizado; seguindo para domínio ou home conforme disponível.")

    except TimeoutException:
        screenshot(driver, "erro_login")
        log.error("Falha no login: timeout ao localizar elementos. Verifique locators.yaml.")
        raise


def selecionar_dominio(driver, preferido=None, timeout=25):
    """Seleciona o domínio após login (se a tela existir)."""
    loc = load_locators("dominio")
    wait = WebDriverWait(driver, timeout)

    # Se não tiver container de domínio, apenas retorne
    try:
        wait_short = WebDriverWait(driver, 3)
        wait_short.until(EC.presence_of_element_located((By.CSS_SELECTOR, loc["container"])))
    except Exception:
        log.info("Tela de seleção de domínio não detectada; prosseguindo.")
        return

    try:
        # Abre o combo (se for o chosen)
        if "combo" in loc:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loc["combo"]))).click()

        # Seleciona a opção (preferida ou primeira)
        if preferido and "opcao" in loc:
            opções = driver.find_elements(By.CSS_SELECTOR, loc["opcao"])
            alvo = None
            for op in opções:
                if preferido.lower() in op.text.lower():
                    alvo = op
                    break
            if not alvo and opções:
                alvo = opções[0]
        else:
            alvo = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loc.get("opcao", ""))))
        if alvo:
            alvo.click()

        # Clica em Entrar/Confirmar
        if "entrar" in loc:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loc["entrar"]))).click()

        # Confirma que entrou (elemento “confirmado”)
        if "confirmado" in loc:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, loc["confirmado"])))

        log.info("Domínio selecionado com sucesso.")

    except TimeoutException:
        screenshot(driver, "erro_dominio")
        log.error("Timeout ao selecionar domínio. Revise seletores em locators.yaml.")
        raise
