"""
Utilitários de navegação para o módulo cadastro_produtos.
Usa seletores centralizados no core/locators.yaml.
"""

from __future__ import annotations
from typing import Iterable, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from core.utils import load_locators

# Carrega seletores do YAML (seção: cadastro_produtos)
LOC = load_locators("cadastro_produtos")

# --- PAGER NUMÉRICO (DevExpress) ---------------------------------
def _pager_click_next_by_number(driver, *, wait_anchor_by=None, wait_anchor_selector=None, wait_timeout=15.0) -> bool:
    """
    Tenta avançar para a próxima página clicando no número (cur+1) do pager DevExpress.
    Retorna True se avançou, False se não há próxima ou não encontrou o link.
    """
    # guarda âncora atual (p/ sincronizar)
    old_anchor = None
    if wait_anchor_by and wait_anchor_selector:
        try:
            old_anchor = driver.find_element(wait_anchor_by, wait_anchor_selector)
        except Exception:
            old_anchor = None

    ok = driver.execute_script(r"""
        try {
            var root  = document.querySelector('#tabPanelResultContainer') || document;
            var pager = root.querySelector('[id*="_DXPagerBottom"], .dxgvPagerBottom, .dxpLite') || root;
            var curEl = pager.querySelector('.dxp-current');
            var cur   = curEl ? parseInt(curEl.textContent.trim(), 10) : NaN;
            if (!isNaN(cur)) {
                var target = String(cur + 1);
                var links  = pager.querySelectorAll('a.dxp-num, a[onclick*="PN"], a[aria-label]');
                for (var i = 0; i < links.length; i++) {
                    var t = (links[i].textContent || '').trim();
                    if (t === target) {
                        links[i].click();
                        return true;
                    }
                }
                // fallback API DevExpress, quando presente:
                if (window.ASPx && ASPx.GVPagerOnClick) {
                    ASPx.GVPagerOnClick('dataGrid', 'PN' + (cur)); // cur=1 => PN1 (vai pra 2)
                    return true;
                }
            }
        } catch(e) {}
        return false;
    """)

    if not ok:
        return False

    # sincroniza nova página (similar ao next_page_once)
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    try:
        if old_anchor:
            WebDriverWait(driver, wait_timeout).until(EC.staleness_of(old_anchor))
        if wait_anchor_by and wait_anchor_selector:
            WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((wait_anchor_by, wait_anchor_selector))
            )
    except TimeoutException:
        # pode ter avançado mesmo assim; tenta heurística simples
        try:
            if wait_anchor_by and wait_anchor_selector:
                new_anchor = driver.find_element(wait_anchor_by, wait_anchor_selector)
                if old_anchor and new_anchor and new_anchor.id != old_anchor.id:
                    return True
        except Exception:
            pass
        return False

    return True


# ---------------------------
# Helpers básicos
# ---------------------------
def _primeiro_visivel(driver: WebDriver, by: By, candidates: Iterable[str]):
    for cand in candidates or []:
        try:
            el = driver.find_element(by, cand)
            if el and el.is_displayed():
                return el
        except Exception:
            continue
    return None


def _clicar_com_fallback(driver: WebDriver, elem):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
    try:
        elem.click()
    except Exception:
        driver.execute_script("arguments[0].click();", elem)


def _esperar_overlays_sumirem(driver: WebDriver, timeout: int = 8):
    """Espera overlays definidos no YAML sumirem (best-effort)."""
    for oid in LOC.get("menu", {}).get("overlay_ids", []):
        try:
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.ID, oid))
            )
            return
        except TimeoutException:
            continue


def _menu_aberto(driver: WebDriver) -> bool:
    """Confirma se o menu está aberto: container visível (e, se possível, com links)."""
    container_ids = LOC.get("menu", {}).get("container_ids", [])
    cont = _primeiro_visivel(driver, By.ID, container_ids)
    if not cont:
        return False
    try:
        links = cont.find_elements(By.CSS_SELECTOR, "a[href]")
        return any(l.is_displayed() for l in links)
    except Exception:
        return True


# ---------------------------
# Abertura do menu (com retry)
# ---------------------------
def abrir_menu_principal(driver: WebDriver, timeout: int = 20, tentativas: int = 5) -> None:
    """
    Garante que o menu principal esteja visível.
    Loop: tenta abrir, espera curto, verifica; repete até 'tentativas'.
    """
    container_ids = LOC.get("menu", {}).get("container_ids", [])
    toggle_ids = LOC.get("menu", {}).get("toggle_ids", [])

    # já está aberto?
    if _menu_aberto(driver):
        _esperar_overlays_sumirem(driver)
        return

    last_err: Optional[Exception] = None
    for _ in range(tentativas):
        for tid in toggle_ids:
            try:
                t = driver.find_element(By.ID, tid)
                _clicar_com_fallback(driver, t)
            except Exception as e:
                last_err = e
                continue

            # pequeno “respiro” e checagem do container
            try:
                WebDriverWait(driver, max(2, timeout // 5)).until(
                    lambda d: _primeiro_visivel(d, By.ID, container_ids) is not None
                )
            except Exception as e:
                last_err = e

        _esperar_overlays_sumirem(driver, timeout=5)
        if _menu_aberto(driver):
            return

    raise TimeoutException(
        f"Não foi possível abrir o menu após {tentativas} tentativas. "
        "Revise 'menu.container_ids' e 'menu.toggle_ids' no locators.yaml."
    ) from last_err


# ---------------------------
# Clique no item Produto/Serviço
# ---------------------------
def _clicar_item_menu_por_href(driver: WebDriver, href: str, timeout: int = 20):
    wait = WebDriverWait(driver, timeout)
    sel = f"a[href='{href}']"
    css_candidates = (
        f"#menus {sel}",
        f"ul#novoMenu {sel}",
        f"nav {sel}",
        sel,
    )
    last_err: Optional[Exception] = None
    for css in css_candidates:
        try:
            link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
            _clicar_com_fallback(driver, link)
            return
        except Exception as e:
            last_err = e
            continue
    raise TimeoutException(f"Item de menu com href={href!r} não encontrado/clicável.") from last_err


def _esperar_tela_produto(driver: WebDriver, timeout: int = 20):
    """Valida chegada na tela de Produto/Serviço, usando os 'checks' do YAML ou fallback padrão."""
    wait = WebDriverWait(driver, timeout)
    checks = LOC.get("produto_servico", {}).get("checks", [])
    if not checks:
        checks = [
            {"by": "css", "value": "form#formProduto, #formProduto"},
            {"by": "xpath", "value": "//h1[contains(.,'Produto')]"},
            {"by": "css", "value": "#tabPanelResultContainer .dxgvTable, #tabPanelResultContainer [id^='dataGrid_DXMainTable']"},
        ]
    conds = []
    for chk in checks:
        by = By.CSS_SELECTOR if (chk.get("by") or "css").lower() == "css" else By.XPATH
        conds.append(EC.visibility_of_element_located((by, chk["value"])))
    wait.until(EC.any_of(*conds))


def ir_para_produto_servico(driver: WebDriver, timeout: int = 20, tentativas_menu: int = 5) -> None:
    """
    Abre o menu com retries; só então clica no item Produto/Serviço.
    Revalida o menu se necessário e confirma a tela de destino.
    """
    abrir_menu_principal(driver, timeout=timeout, tentativas=tentativas_menu)

    hrefs = LOC.get("produto_servico", {}).get("hrefs", [])
    last_err: Optional[Exception] = None
    for path in hrefs:
        try:
            if not _menu_aberto(driver):
                abrir_menu_principal(driver, timeout=timeout, tentativas=tentativas_menu)
            _clicar_item_menu_por_href(driver, path, timeout=timeout)
            _esperar_overlays_sumirem(driver)
            _esperar_tela_produto(driver, timeout=timeout)
            return
        except Exception as e:
            last_err = e
            continue

    raise TimeoutException(
        "Falha ao abrir a tela 'Produto/Serviço'. "
        "Revise 'produto_servico.hrefs' e 'produto_servico.checks' no locators.yaml."
    ) from last_err


__all__ = ["abrir_menu_principal", "ir_para_produto_servico"]
