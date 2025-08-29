# extrair_aliquota.py
"""
Submódulo: extrair_aliquota
Coleta dados da grid de produtos (aba de resultados) e exporta CSV/JSON.

Lê seletores de core/locators.yaml (cadastro_produtos.tabs / cadastro_produtos.grid / cadastro_produtos.pagination).
"""

from __future__ import annotations
from typing import Iterable, Optional
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

from core.pagination import next_page_once
from core import utils
from core._ui import prompt_paginas_extracao

from .._navigate import abrir_menu_principal, ir_para_produto_servico

# ---------------------------
# Helpers para YAML selectors
# ---------------------------
BY_MAP = {
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "id": By.ID,
    "name": By.NAME,
    "link": By.LINK_TEXT,
    "partial_link": By.PARTIAL_LINK_TEXT,
    "tag": By.TAG_NAME,
    "class": By.CLASS_NAME,
}

def _as_tuple(selector_info):
    """
    Aceita:
      - {"by": "css", "value": ".seletor"}
      - {"by": "css", "value": [".a", ".b"]} -> pega o primeiro
    Retorna: (By.*, "selector") ou (None, None) se vier vazio.
    """
    if not selector_info:
        return None, None
    by_str = (selector_info.get("by") or "css").lower()
    by = BY_MAP.get(by_str, By.CSS_SELECTOR)
    value = selector_info.get("value")
    if isinstance(value, list):
        value = value[0] if value else None
    return by, value

# ---------------------------
# UI helpers
# ---------------------------
def _first_clickable(wait: WebDriverWait, by: str, selectors: Iterable[str]):
    last_err = None
    for sel in selectors:
        try:
            return wait.until(EC.element_to_be_clickable((by, sel)))
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    return None

def _ativar_aba_resultados(driver: WebDriver, loc: dict, timeout: int = 20) -> None:
    tabs_cfg = (loc or {}).get("tabs", {}) or {}
    candidates = tabs_cfg.get("result_tab", []) or []
    if not candidates:
        return
    wait = WebDriverWait(driver, timeout)
    try:
        btn = _first_clickable(wait, By.CSS_SELECTOR, candidates)
        try:
            btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn)
        WebDriverWait(driver, 3).until(lambda d: True)  # pequeno settle
    except Exception:
        pass  # se não achou/ativou, segue assim mesmo

# ---------------------------
# Coleta da grid
# ---------------------------
def _coletar_dados_tabela(driver: WebDriver, loc: dict, timeout: int = 25) -> list[dict]:
    wait = WebDriverWait(driver, timeout)
    grid_cfg = (loc or {}).get("grid", {}) or {}

    container_css = grid_cfg.get("container_css", []) or ["#gridProdutos", "table#gridProdutos"]
    header_css    = grid_cfg.get("header_css", [])    or ["thead th"]
    row_css       = grid_cfg.get("row_css", [])       or ["tbody tr"]

    # 1) Melhor chance de estar na aba certa
    _ativar_aba_resultados(driver, loc, timeout=max(10, timeout // 2))

    # 2) Container da grid
    grid = None
    last_err = None
    for sel in container_css:
        try:
            grid = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, sel)))
            break
        except Exception as e:
            last_err = e
            continue
    if not grid:
        raise TimeoutException("Grid não localizada. Ajuste 'cadastro_produtos.grid.container_css' no YAML.") from last_err

    # 3) Cabeçalhos
    headers: list[str] = []
    for hsel in header_css:
        try:
            headers = [th.text.strip() for th in grid.find_elements(By.CSS_SELECTOR, hsel)]
            headers = [h for h in headers if h]
            if headers:
                break
        except Exception:
            continue

    # 4) Linhas
    rows = []
    for rsel in row_css:
        try:
            rows = grid.find_elements(By.CSS_SELECTOR, rsel)
            if rows:
                break
        except Exception:
            continue

    # 5) Montagem dos registros
    registros: list[dict] = []
    for row in rows:
        cols = [td.text.strip() for td in row.find_elements(By.CSS_SELECTOR, "td")]
        if not any(cols):
            continue

        if headers and len(headers) == len(cols):
            d = dict(zip([h.lower() for h in headers], cols))
        else:
            d = {f"col_{i+1}": v for i, v in enumerate(cols)}
        registros.append(d)

    return registros

# ---------------------------
# Orquestração
# ---------------------------
def _na_tela_produto(driver) -> bool:
    try:
        WebDriverWait(driver, 5).until(EC.any_of(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "form#formProduto, #formProduto")),
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#tabPanelResultContainer .dxgvTable, #tabPanelResultContainer [id^='dataGrid_DXMainTable']")),
            EC.visibility_of_element_located((By.XPATH, "//h1[contains(.,'Produto')]")),
        ))
        return True
    except Exception:
        return False
    
# --- PAGER NUMÉRICO (DevExpress): vai para a próxima página clicando no número (cur+1)
def _pager_click_next_by_number(
    driver,
    *,
    wait_anchor_by=None,
    wait_anchor_selector=None,
    wait_timeout: float = 15.0
) -> bool:
    """
    Retorna True se conseguiu avançar de página clicando no número (cur+1).
    Fallback para ASPx.GVPagerOnClick quando disponível.
    Sincroniza a troca usando a âncora (se fornecida).
    """
    # guarda âncora atual para sincronizar a mudança
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
                    if (t === target) { links[i].click(); return true; }
                }
                // fallback oficial DevExpress
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

    # sincronização da nova página (sem depender do YAML do "next")
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


def executar(driver):
    if not _na_tela_produto(driver):
        abrir_menu_principal(driver)
        ir_para_produto_servico(driver)
    loc = utils.load_locators("cadastro_produtos")

    pag = (loc or {}).get("pagination", {}) or {}
    next_by, next_sel = _as_tuple(pag.get("next"))
    anchor_by, anchor_sel = _as_tuple(pag.get("anchor"))

    if not next_by or not next_sel:
        raise RuntimeError(
            "Locators de paginação ausentes. Defina 'cadastro_produtos.pagination.next' no locators.yaml"
        )

    # --- Pergunta ao usuário ---
    max_pages = prompt_paginas_extracao(driver)
    if max_pages is None:
        utils.log.info("Extração de alíquotas cancelada pelo usuário.")
        return

    # --- INÍCIO DA EXTRAÇÃO ---
    pagina = 1
    todos_registros = []
    while True:
        utils.log.info(f"Extraindo página {pagina}...")
        registros = _coletar_dados_tabela(driver, loc)
        utils.log.info(f"Registros extraídos nesta página: {len(registros)}")
        todos_registros.extend(registros)

        # Controle de páginas
        if max_pages is True:
            avancou = next_page_once(
                driver,
                next_by=next_by,
                next_selector=next_sel,
                wait_anchor_by=anchor_by,
                wait_anchor_selector=anchor_sel,
            )
            if not avancou:
                break
        else:
            if pagina >= max_pages:
                break
            avancou = next_page_once(
                driver,
                next_by=next_by,
                next_selector=next_sel,
                wait_anchor_by=anchor_by,
                wait_anchor_selector=anchor_sel,
            )
            if not avancou:
                break
        pagina += 1

    utils.log.info(f"Extração finalizada. Total de registros: {len(todos_registros)}")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    nome_arquivo = f"produtos_{timestamp}"
    utils.salvar_csv(nome_arquivo, todos_registros)
    utils.salvar_json(nome_arquivo, todos_registros)
