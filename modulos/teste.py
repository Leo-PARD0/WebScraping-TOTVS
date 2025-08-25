# modulos/teste.py
"""
Módulo de teste básico.
- Verifica rapidamente se parece estar logado e dentro do domínio.
- Não altera nada no sistema: apenas checagens leves e prints.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# opcional: carregar seletores do YAML para checagens mais robustas
from core.utils import load_locators

def executar(driver, **kwargs):
    wait = WebDriverWait(driver, 20)
    loc_login = load_locators("login") or {}
    loc_dom   = load_locators("dominio") or {}

    ok_login = False
    ok_dom   = False

    # 1) Tenta detectar “pós-login”
    after_login_sel = loc_login.get("after_login", "ul#novoMenu")
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, after_login_sel)))
        ok_login = True
        print("[OK] Elemento de pós-login detectado:", after_login_sel)
    except Exception:
        print("[!] Não foi possível confirmar pós-login via seletor:", after_login_sel)

    # 2) Tenta detectar “confirmação de domínio” (se existir no YAML)
    confirmado_sel = loc_dom.get("confirmado", None)  # ex.: "ul#novoMenu"
    if confirmado_sel:
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, confirmado_sel)))
            ok_dom = True
            print("[OK] Domínio confirmado via seletor:", confirmado_sel)
        except Exception:
            print("[!] Não foi possível confirmar domínio via seletor:", confirmado_sel)
    else:
        # Se não houver chave "confirmado", considere que login basta para o smoke test
        ok_dom = ok_login

    # 3) Resultado final do smoke test
    if ok_login and ok_dom:
        print("✅ Módulo de teste executado com sucesso (login + domínio parecem OK).")
    elif ok_login:
        print("⚠️ Login parece OK, mas não confirmamos domínio.")
    else:
        print("❌ Não conseguimos confirmar nem login nem domínio. Revise os seletores em core/locators.yaml.")
