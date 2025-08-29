# core/pagination.py
from __future__ import annotations
import logging
import time
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

log = logging.getLogger("pagination")

def _find(driver: WebDriver, by: By, sel: str, timeout: float) -> WebElement:
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, sel)))

def _is_disabled(elem: WebElement) -> bool:
    try:
        if (elem.get_attribute("disabled") is not None) or \
           (elem.get_attribute("aria-disabled") or "").lower() in ("true", "1"):
            return True
        cls = elem.get_attribute("class") or ""
        return any(flag in cls.split() for flag in ("disabled","p-disabled","is-disabled"))
    except StaleElementReferenceException:
        return True

def _safe_click(driver: WebDriver, elem: WebElement) -> bool:
    try:
        elem.click()
        return True
    except (ElementClickInterceptedException, StaleElementReferenceException):
        try:
            driver.execute_script("arguments[0].click();", elem)
            return True
        except Exception:
            return False

def next_page_once(
    driver: WebDriver,
    *,
    next_by: By,
    next_selector: str,
    wait_anchor_by: Optional[By] = None,
    wait_anchor_selector: Optional[str] = None,
    wait_timeout: float = 15.0,
    sleep_after_click: float = 0.4,
    scroll_into_view: bool = True,
) -> bool:
    """
    Tenta avançar UMA página.
    Retorna:
      True  -> avançou (página mudou)
      False -> não avançou (fim da paginação, botão desabilitado/ausente ou erro de clique)

    Parâmetros:
    - next_by/next_selector: seletor do botão 'Próxima'.
    - wait_anchor_*: seletor de um elemento que exista por página (ex.: primeira linha da tabela).
      Usado para sincronizar a mudança de página.
    """
    try:
        btn = _find(driver, next_by, next_selector, timeout=5)
    except TimeoutException:
        log.info("pagination | Botão 'Próxima' não encontrado.")
        return False

    if _is_disabled(btn):
        log.info("pagination | Botão 'Próxima' está desabilitado (provável última página).")
        return False

    # Captura o número da página antes do clique
    old_page_num = None
    old_anchor = None
    if wait_anchor_by and wait_anchor_selector:
        try:
            old_page_elem = driver.find_element(wait_anchor_by, wait_anchor_selector)
            old_page_num = old_page_elem.text.strip()
            old_anchor = old_page_elem
        except Exception:
            old_page_num = None
            old_anchor = None

    if scroll_into_view:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        except Exception:
            pass

    if not _safe_click(driver, btn):
        log.warning("pagination | Falha ao clicar em 'Próxima'.")
        return False

    time.sleep(sleep_after_click)  # animações/spinner breves

    # Espera o número da página mudar
    if wait_anchor_by and wait_anchor_selector and old_page_num is not None:
        def _safe_anchor_check(d):
            try:
                elem = d.find_element(wait_anchor_by, wait_anchor_selector)
                return elem.text.strip() != old_page_num
            except StaleElementReferenceException:
                return False  # Tenta de novo até timeout

        try:
            WebDriverWait(driver, wait_timeout).until(_safe_anchor_check)
        except TimeoutException:
            # pode ter avançado mesmo assim; checa heurística
            try:
                if wait_anchor_by and wait_anchor_selector:
                    new_anchor = driver.find_element(wait_anchor_by, wait_anchor_selector)
                    if old_anchor and new_anchor and new_anchor.id != old_anchor.id:
                        return True
            except Exception:
                pass
            return False

    return True
